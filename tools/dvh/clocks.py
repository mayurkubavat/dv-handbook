"""clocks.py -- clock tree, reset tree and crossing report from a flattened
netlist (see design.py).

The walks follow a net backwards from a register's clock (or reset) pin to
its source. A source is a top-level input port or a register output (a
divided or generated clock). Buffers, inverters, gates and multiplexers are
walked through and recorded. A net with more than one driver -- two
tri-state assignments selecting a clock -- is refused as a design the tool
cannot answer for, rather than walked through whichever driver came last.

A clock walk has to tell a gate's clock input from its enable, or every
gated register lands in a domain of its own and an ordinary synchronous path
across a clock gate is reported as a crossing. Nothing in a netlist settles
that: `clk & en` and `clk1 & clk2` are the same gate. So the walk has two
modes. Undeclared, it scores evidence -- a net that drives a clock pin
directly is strong, a port or a register output is weak -- and wherever it
would have to demote an input that could itself be a clock, it reports the
gate as undecided instead. Declared (`--clock`), it asks `clock_deps` which
declared clocks each input depends on, which is a definition rather than a
guess: control depends on nothing the gate lacks, a blend depends on
something it does. Demoted inputs are recorded in `through`, and the ports
among them are listed in the report.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .design import (ASYNC_RESET_TYPES, DFF_TYPES, SYNC_RESET_TYPES,
                     Module, registers)

# Combinational cell types the walks pass through.
PASS_THROUGH = {"$not", "$and", "$or", "$xor", "$mux", "$pmux", "$logic_not",
                "$logic_and", "$logic_or", "$_BUF_", "$_NOT_", "$_AND_",
                "$_OR_", "$_MUX_", "$reduce_or", "$reduce_and", "$eq", "$ne"}

# Latches are state elements, not combinational logic. A path through one is
# never direct, so it can never be a synchronizer; but stopping at a latch
# would hide the crossing behind it, so the data walk passes through and
# records the latch. Only the clock walk stops here.
LATCH_TYPES = {"$dlatch", "$adlatch", "$dlatchsr", "$sr",
               "$_DLATCH_P_", "$_DLATCH_N_", "$_SR_PP_", "$_SR_NN_"}

MUX_TYPES = ("$mux", "$pmux", "$_MUX_")


@dataclass
class Source:
    name: str            # port name or register name
    kind: str            # "port" | "register" | "constant" | "unknown"
    bit: object = None   # the net the walk ended on, as the netlist numbers it
    through: list = field(default_factory=list)   # cell types walked through


def clock_candidates(mod: Module, declared=()) -> tuple:
    """Two tiers of evidence that a net is carrying a clock, not control.

    At a gate feeding a clock pin, one input is the clock and the others are
    enables, and nothing in the netlist says which. Two signals separate them
    most of the time. **Strong**: the net already drives some register's
    clock pin directly, or is a register output used as a clock (a divider),
    or is something the netlist cannot see into, which is what an analog
    block looks like from here. **Weak**: it is an input port, a register's
    output or a latch's, any of which a clock can be and an enable, a
    divider or a held enable can be too.

    Strong evidence for one input is not evidence against another. Both a
    clock gate and Plassan's *blending* -- two clocks combined to make a
    third -- are one gate with one input that drives registers elsewhere and
    one that does not, and nothing in the netlist separates them. So where
    the walk demotes an input that is itself a clock candidate, it says the
    choice was a guess rather than making it silently; an earlier version
    reported a blended clock as "one clock, gated differently" and passed
    the build on an unsynchronized crossing between two unrelated clocks.

    That is not a defect in the tool; it is @sec-ch03-clocks' point that the
    relationship between clocks is a property of the specification. Declare
    the clocks -- `--clock` on the command line -- and the evidence is
    replaced by a *definition*, below, so the question does not arise.
    """
    if declared:
        return CLOCK_BITS, frozenset(declared)
    strong, used_as_clock = set(), set()
    for _, cell in registers(mod):
        for b in cell.conns.get("CLK", []):
            if isinstance(b, int):
                used_as_clock.add(b)
                if b in mod.port_of_bit:
                    strong.add(mod.port_of_bit[b])
    for name, cell in registers(mod):
        if any(b in used_as_clock for b in cell.conns.get("Q", [])):
            strong.add(name)          # a divided or generated clock
    weak = {p for p, v in mod.ports.items() if v["direction"] == "input"}
    return strong, weak


# Sentinel in the `strong` slot: the pair carries a set of clock *bits*
# computed from a declaration rather than two tiers of evidence.
CLOCK_BITS = object()


def clock_ports(mod: Module) -> set:
    """Input ports that drive some register's clock pin with no logic between.

    Whatever else is a clock, these are: it is the one statement about clocks
    a netlist makes on its own. A declaration that leaves one of them out is
    incomplete, and the run is then quieter than an undeclared one.
    """
    return {mod.port_of_bit[b] for _, cell in registers(mod)
            for b in cell.conns.get("CLK", [])
            if isinstance(b, int) and b in mod.port_of_bit}


# A dependency the netlist cannot resolve: a black box, a memory, an undriven
# net. It is not the same answer as "depends on no clock", and treating it
# as that answer made a phase-locked loop's output -- the chapter's own
# example of a primary clock -- into gating control.
UNKNOWN = "?"


# The pins a register samples on its clock edge. Every *other* input can
# change the output on its own timing: the clock, an asynchronous set,
# clear or load, and the value an asynchronous load makes the output
# follow while the load is high. The list is of what is excluded, because
# the two lists of what was included -- first the clock alone, then the
# clock and the asynchronous controls -- were each outgrown by the next
# register pin a design used.
SYNCHRONOUS_PINS = ("D", "EN", "SRST")


def _timing_pins(cell) -> list:
    """Every input of a register that can change its output on its own
    timing rather than on the clock's: the clock, and everything not
    sampled by it."""
    return [p for p, d in cell.dirs.items()
            if d == "input" and p not in SYNCHRONOUS_PINS]


def clock_deps(mod: Module, bit, declared,
               through_registers=True) -> frozenset:
    """Which declared clocks a net's value depends on, as clock port *bits*.

    This replaces the question the evidence heuristic kept getting wrong.
    "Is this net a clock?" has no answer in a netlist: `clk & en` and
    `clk1 & clk2` are the same gate. "Which declared clocks does this net
    depend on?" is a definition, and it separates the two cases by itself.

    A bit of a declared clock port depends on itself -- the bit, because
    every bit of a vector port shares the port's name and a divider of
    `lane_clk[1]` is not a divider of `lane_clk[0]`. A register's output
    depends on whatever every input it does not sample on its clock
    depends on -- the clock, an asynchronous set, clear or load, and the
    value a load makes it follow -- which makes a divided clock a
    dependent of the clock that divides it to any depth; a latch's output
    depends on its enable and its data; with `through_registers` false the
    walk stops at either, answering the narrower question "which clocks
    reach here through logic alone". Any combinational cell depends on the
    union of its inputs. An undeclared
    port depends on nothing. Anything the netlist cannot see into depends
    on `UNKNOWN`, which is never mistaken for nothing.

    At a gate feeding a clock pin -- a multiplexer's select included --
    the inputs that reach a declared clock through logic alone are the
    gate's clocks. Every other input is compared against them: one that
    depends on nothing, or only on clocks the gate already has, is
    synchronous control -- an enable, or a divider of the
    same clock -- and the result is one domain gated, which is what a clock
    gate is. One that depends on a clock the gate does not have, or on
    something unknown, makes a blend: a new domain, which is what
    @sec-ch03-clocks says blending is. No shape has to be recognized.

    Iterative, with the clock pins of registers on the same worklist: a
    twelve-hundred-stage ripple counter feeding a gate ended a recursive
    version with `RecursionError`.
    """
    out, seen, stack = set(), set(), [bit]
    while stack:
        b = stack.pop()
        if not isinstance(b, int) or b in seen:
            continue
        seen.add(b)
        if mod.port_of_bit.get(b) in declared:
            out.add(b)
            continue
        if b in mod.port_of_bit:            # an undeclared port: control
            continue
        drv = mod.drivers.get(b)
        if drv is None:
            out.add(UNKNOWN)
            continue
        cell = mod.cells[drv[0]]
        if cell.type in DFF_TYPES:
            if through_registers:
                stack += [x for pin in _timing_pins(cell)
                          for x in cell.conns.get(pin, [])]
            continue
        if cell.type in LATCH_TYPES:
            if through_registers:
                stack += [x for p, bs in cell.conns.items()
                          if cell.dirs.get(p) == "input" for x in bs]
            continue
        if cell.type.startswith("$") and not cell.type.startswith("$mem"):
            stack += [x for p, bs in cell.conns.items()
                      if cell.dirs.get(p) == "input" for x in bs]
            continue
        out.add(UNKNOWN)                    # a black box, a memory
    return frozenset(out)


def _tier(mod: Module, bit, strong, weak, any_comb) -> int:
    """2 for strong evidence of a clock, 1 for weak, 0 for none.

    Only the undeclared walk uses tiers. Where the clocks are declared the
    walk asks `clock_deps` instead, and there is nothing to score.
    """
    srcs = _walk_to_sources(mod, bit, set(), any_comb, None)
    if any(s.name in strong or s.kind == "unknown" for s in srcs):
        return 2
    # A register output is weak evidence exactly as a port is: a divider
    # and an enable register are the same shape, and demoting one of them
    # in silence excused a clock blended with a divided clock from the gate.
    return 1 if any(s.name in weak or s.kind in ("register", "latch")
                    for s in srcs) else 0


def _walk_to_sources(mod: Module, bit, seen=None, any_comb=False,
                     clock_roots=None) -> list[Source]:
    """All sources reachable backwards from `bit` through combinational logic.

    With any_comb=True every combinational cell is walked (data cones);
    otherwise only the clock-tree pass-through set is (clock and reset nets).
    `clock_roots` is the (strong, weak) pair from `clock_candidates`, or
    the `CLOCK_BITS` sentinel with the declared clock names; a gate then
    follows only the inputs that carry a clock, so an enable does not join
    the domain name.

    A worklist, not a recursion: each entry carries the cells and gating
    the path passed, so a fifteen-hundred-gate chain does not end the run
    with `RecursionError`. `through` is read as a set everywhere, so the
    order in which the tokens accumulate does not matter.
    """
    seen = seen if seen is not None else set()
    out = []
    stack = [(bit, (), clock_roots)]
    while stack:
        b, toks, roots = stack.pop()

        def emit(name, kind):
            out.append(Source(name, kind, b, list(dict.fromkeys(toks))))
        if not isinstance(b, int):
            emit(f"const {b}", "constant")
            continue
        if b in seen:
            continue
        seen.add(b)
        if b in mod.port_of_bit:
            emit(mod.port_of_bit[b], "port")
            continue
        drv = mod.drivers.get(b)
        if drv is None:
            emit(mod.net(b), "unknown")
            continue
        cell = mod.cells[drv[0]]
        if cell.type in DFF_TYPES:
            emit(mod.reg_of_bit.get(b, mod.net(cell.conns["Q"][0])),
                 "register")
            continue
        combinational = not cell.type.startswith("$mem")
        if cell.type in LATCH_TYPES and any_comb:
            # A latch is a state element, so a path through one is not
            # direct and cannot be a synchronizer; but the crossing behind
            # it is still a crossing, so the walk continues rather than
            # stopping here. Every input counts, not just the data: a
            # register in one domain driving a latch's *enable*, with the
            # latch's output sampled in another, is a crossing.
            pushed = False
            for port in _data_inputs(cell):
                for x in cell.conns.get(port, []):
                    stack.append((x, toks + (cell.type,), roots))
                    pushed = True
            if not pushed:
                emit(mod.net(b), "latch")
            continue
        if cell.type in LATCH_TYPES:
            emit(mod.net(b), "latch")
            continue
        if cell.type in PASS_THROUGH or (any_comb and combinational):
            ins, control, ambiguous, roots = _classify_gate(
                mod, cell, any_comb, roots)
            more = (cell.type,) + (("mux",) if cell.type in MUX_TYPES else ())
            more += tuple(f"gated by {c}" for c in sorted(set(control)))
            if ambiguous:
                more += ("ambiguous: clock not distinguishable here",)
            for _, x in ins:
                stack.append((x, toks + more, roots))
            continue
        emit(f"{mod.net(b)} (driven by {cell.type})", "unknown")
    return out


def _classify_gate(mod: Module, cell, any_comb, clock_roots):
    """Which inputs of a gate on a clock path carry the clock.

    Returns (inputs to follow, nets demoted to control, ambiguous, the roots
    to carry on with). Only the clock walk demotes anything: a data cone
    follows every input.
    """
    told = bool(clock_roots) and clock_roots[0] is CLOCK_BITS
    # Undeclared, a multiplexer's select is skipped: a select is not a clock
    # and the walk has no way to say more. Declared, the select is an input
    # like any other, and the dependency rule decides -- a second clock on
    # the select is a blend exactly as it would be on a gate input, and
    # skipping it excused four such designs from the build gate.
    skip_select = not any_comb and cell.type in MUX_TYPES and not told
    ins = [(port, b) for port, bits in cell.conns.items()
           if cell.dirs.get(port) == "input"
           and not (skip_select and port == "S")
           for b in bits]
    control, ambiguous = [], False
    if not clock_roots:
        return ins, control, ambiguous, clock_roots
    if cell.type in MUX_TYPES and not any_comb and not told:
        # @sec-ch03-clocks separates gating from selection, and the walk
        # has to as well. A gate has one clock and an enable, so demoting
        # an input to control is right. A multiplexer selects between two
        # clocks, so demoting either is wrong; where its inputs disagree,
        # the clock is undecided and says so.
        roots = {s.name for (p, b) in ins
                 for s in _walk_to_sources(mod, b, set(), False, None)}
        return ins, control, len(roots) > 1, None
    if told:
        # Declared: which clocks each input depends on settles it, and an
        # input depending on none of them is control. An input that depends
        # on something the netlist cannot see into is never control: it may
        # be a clock, and the gate is then a blend.
        declared = clock_roots[1]
        direct = {(p, b): clock_deps(mod, b, declared, False)
                  for (p, b) in ins}
        have = frozenset().union(*direct.values()) - {UNKNOWN}
        if any(direct.values()):
            carrying = [(p, b) for (p, b) in ins
                        if direct[(p, b)]
                        or UNKNOWN in clock_deps(mod, b, declared)
                        or not clock_deps(mod, b, declared) <= have]
        else:
            # No input reaches a clock through logic alone: every candidate
            # here is a register output, and a divider and an enable
            # register are the same shape. Undecided, and loud.
            carrying = [(p, b) for (p, b) in ins
                        if clock_deps(mod, b, declared)]
            ambiguous = len(carrying) > 1
        if carrying and len(carrying) < len(ins):
            control = [mod.net(b) for (p, b) in ins
                       if (p, b) not in carrying and isinstance(b, int)]
            ins = carrying
        return ins, control, ambiguous, clock_roots
    strong, weak = clock_roots
    tiers = [(_tier(mod, b, strong, weak, any_comb), p, b) for (p, b) in ins]
    best = max((t for t, _, _ in tiers), default=0)
    carrying = [(p, b) for (t, p, b) in tiers if t == best]
    if best and len(carrying) < len(ins):
        # A constant is not gating control worth naming: a tied-off input
        # is part of the gate, and "gated by const z" told a reader nothing.
        control = [mod.net(b) for (p, b) in ins
                   if (p, b) not in carrying and isinstance(b, int)]
        # Demoting an input that is itself a clock candidate is a guess,
        # not a finding: a gate blending two clocks and a gate enabling one
        # look identical here.
        ambiguous = any(t >= 1 for (t, p, b) in tiers
                        if (p, b) not in carrying)
        ins = carrying
    elif best and len(carrying) > 1:
        # More than one input could be a clock and nothing in the netlist
        # chooses between them. Say so instead of choosing, at any tier.
        ambiguous = True
    return ins, control, ambiguous, clock_roots


def _domain_key(mod: Module, cell, srcs, ambiguous: bool, name: str) -> str:
    """What makes two registers members of one clock domain.

    Identity is the *net* a clock arrives on, not the names of the sources
    the walk reached. Names collide: two clock multiplexers selecting the
    same pair of inputs produce two networks whose source names are equal
    and whose clocks are opposite, and a name-based key merged them into one
    domain and dropped the crossing between them. This was the root of a
    defect that reappeared in three consecutive reviews, in three different
    lines, and each earlier fix removed a consequence of it rather than the
    cause.

    A register whose clock the walk could not resolve gets an identity of
    its own, derived from the register, so it is equal to nothing and its
    crossings can never be dropped by a comparison.
    """
    if ambiguous:
        return f"undecided clock of {name}"
    bits = [b for b in cell.conns.get("CLK", []) if isinstance(b, int)]
    label = "+".join(sorted({s.name for s in srcs})) or mod.net(bits[0])
    # The label is for a person; the net keeps two same-named networks apart.
    return f"{label}" if len(bits) != 1 else f"{label}#{bits[0]}"


def _pretty(key: str) -> str:
    """The part of a domain key a reader should see."""
    return key.split("#")[0]


def clock_tree(mod: Module, declared=()) -> dict:
    """Registers grouped by clock source; each register with its clock path.

    `declared` is the design's clock names, from the specification. Given
    them, the walk stops guessing which input of a gate is the clock.
    """
    regs = {}
    prim = clock_candidates(mod, declared)
    for name, cell in registers(mod):
        srcs = _walk_to_sources(mod, cell.conns["CLK"][0], None, False, prim)
        roots = sorted({s.name for s in srcs})
        gated = any(s.through for s in srcs)
        through = sorted({t for s in srcs for t in s.through})
        unsure = any(t.startswith("ambiguous") for t in through)
        # Root *bits*, not names. A vector clock port gives every one of
        # its bits the same source name, so comparing names made two clocks
        # on one port look like one clock. The bits come from the same walk
        # that produced the names, so the two can never disagree about which
        # inputs of a gate carried the clock.
        root_bits = sorted({str(src.bit) for src in srcs})
        regs[name] = {"clock_sources": roots, "gated_or_muxed": gated,
                      "through": through, "src": cell.src,
                      "clock_ambiguous": unsure,
                      "root_bits": root_bits,
                      "domain": _domain_key(mod, cell, srcs, unsure, name)}
    domains = {}
    for name, info in regs.items():
        domains.setdefault(info["domain"], []).append(name)
    # Every input port the walk demoted to gating control at a gate feeding
    # a clock pin, printed so a reader can see a clock among them. The
    # completeness check on a declaration can only know a clock that drives
    # a clock pin directly; a clock that only ever appears gated is, to the
    # netlist, an enable, and the one defense is to say which ports were
    # read that way.
    demoted = {t.removeprefix("gated by ")
               for info in regs.values() for t in info["through"]
               if t.startswith("gated by ")}
    by_name = dict(registers(mod))
    control = set()
    latches = {mod.net(c.conns["Q"][0]): c for c in mod.cells.values()
               if c.type in LATCH_TYPES and c.conns.get("Q")}
    for net in demoted:
        if net in mod.ports:
            control.add(net)
            continue
        # A demoted register or latch is reported by the ports that time
        # it, because that is where a hidden clock would be: a clock that
        # only ever reaches the gate through a register, or through a
        # latch it holds open, demotes no port itself.
        if net in by_name:
            cell = by_name[net]
            bits = [x for pin in _timing_pins(cell)
                    for x in cell.conns.get(pin, [])]
        elif net in latches:
            cell = latches[net]
            bits = [x for pin in _data_inputs(cell)
                    for x in cell.conns.get(pin, [])]
        else:
            continue
        for b in bits:
            control |= {src.name for src in
                        _walk_to_sources(mod, b, None, False, None)
                        if src.kind == "port"}
    # A declared clock is not a finding here: a clock gate whose enable is
    # a register on that same clock demotes the register, and the port
    # that clocks it is the declared clock. The list is for the clocks a
    # declaration missed.
    control = sorted(control - set(declared))
    return {"domains": {k: sorted(v) for k, v in domains.items()},
            "registers": regs, "ports_treated_as_control": control}


# The control pin that forces a register to a value, per kind of register
# the netlist can produce, most specific first: a register with both a set
# and a clear is reported by its clear. The pin is looked for on the cell
# rather than deduced from its type, because the deduction was wrong the
# first time a design used a register type it had not anticipated -- an
# asynchronous *load*, whose pins are ALOAD and AD, was classified as an
# asynchronous reset and then looked for a CLR pin that does not exist.
# An asynchronous load is reported as what it is: it forces a value, not a
# constant, so it is not a reset and a reader should not read it as one.
RESET_PINS = (("CLR", "CLR_POLARITY", "asynchronous"),
              ("ARST", "ARST_POLARITY", "asynchronous"),
              ("SET", "SET_POLARITY", "asynchronous set"),
              ("ALOAD", "ALOAD_POLARITY", "asynchronous load"),
              ("SRST", "SRST_POLARITY", "synchronous"))


def reset_tree(mod: Module, declared=()) -> dict:
    """Every register's reset: kind, polarity, source; and the ones without."""
    out, none = {}, []
    for name, cell in registers(mod):
        found = [r for r in RESET_PINS if r[0] in cell.conns]
        if found:
            pin, polarity, kind = found[0]
            pol = cell.params.get(polarity, "1")
        else:
            if cell.type in ASYNC_RESET_TYPES | SYNC_RESET_TYPES:
                raise AssertionError(
                    f"{cell.type} is listed as a register with a reset but "
                    f"carries none of {[r[0] for r in RESET_PINS]}; add its "
                    "pin to RESET_PINS rather than letting it read as "
                    "unreset")
            # The unreset registers are the finding a reader acts on, so
            # they carry a location like every other finding.
            none.append({"name": name, "src": cell.src})
            continue
        def control(pin, polarity, kind):   # noqa: PLR1704
            srcs = []
            for b in cell.conns[pin]:       # set and reset are per-bit
                # A reset net is not a clock net, and walking it with the
                # clock walk answered the wrong question twice. That walk
                # skips a multiplexer's select, because a select is not a
                # clock -- but Yosys builds an ordinary set/reset flip-flop's
                # CLR net as a multiplexer whose *select is the reset*, so
                # the reported source was a pair of constants and the reset
                # signal was never named. It also demotes gate inputs and
                # reports a clock it could not resolve, so a soft reset came
                # back as gating control and a reset report carried the
                # sentence "clock not distinguishable here".
                srcs += _walk_to_sources(mod, b, None, True, None)
            pol = cell.params.get(polarity, "1")
            named = sorted({s.name for s in srcs if s.kind != "constant"})
            return {"pin": pin, "kind": kind,
                    "active": "high" if str(pol).endswith("1") else "low",
                    # The constants a lowered set/reset net is built from are
                    # not its source; the signal steering them is.
                    "sources": named or sorted({s.name for s in srcs}),
                    "through": sorted({t for s in srcs for t in s.through})}

        # A register can carry more than one, and `$dffsr` carries two: an
        # asynchronous set and an asynchronous clear. Reporting only the
        # first left the other's source out of the report entirely.
        controls = [control(*r) for r in found]
        out[name] = dict(controls[0], controls=controls, src=cell.src)
        del out[name]["pin"]
        # A register whose only forcing control is a set or a load has no
        # reset, so it belongs in the list a reader acts on as well. The
        # report once said a design had no unreset registers when its one
        # register had no reset -- the JSON was honest and the human report
        # was not.
        if not any(c["kind"] in ("asynchronous", "synchronous")
                   for c in controls):
            none.append({"name": name, "src": cell.src})
    return {"registers": out,
            "no_reset": sorted(none, key=lambda r: r["name"])}


def _data_inputs(cell) -> list:
    """Every input of a cell except its clock.

    Enumerated from the netlist rather than named, because a hand-written
    list is wrong the first time the netlist produces a cell the list did
    not anticipate. Two separate crossings went unreported that way: one
    arriving on a latch's enable, and one folded onto a flip-flop's
    synchronous reset by an optimization added for an unrelated reason. The
    clock is excluded because a value arriving on it is a clock question,
    which the clock walk answers.
    """
    return [p for p, d in cell.dirs.items()
            if d == "input" and p not in ("CLK",)]


def _data_cone_registers(mod: Module, cell) -> set[str]:
    """Registers reaching any of this register's data inputs, through logic.

    Iterative, which the general walk cannot be: that one prefixes each cell
    type onto the path it came by, so its answer depends on the route, while
    this one only asks which registers are back there. A fifteen-hundred-deep
    exclusive-or chain -- which nothing can collapse -- ended the run with a
    `RecursionError` when this recursed.

    Deliberately not cached. A first attempt stored each pass's whole result
    against every net the pass touched, which is an over-approximation, and
    it promptly invented three crossings in the book's own example design.
    The cost that made caching tempting was somewhere else: see
    `_feeds_directly`.
    """
    found, seen, stack = set(), set(), []
    for port in _data_inputs(cell):
        stack += list(cell.conns.get(port, []))
    while stack:
        bit = stack.pop()
        if not isinstance(bit, int) or bit in seen:
            continue
        seen.add(bit)
        if bit in mod.port_of_bit or bit not in mod.drivers:
            continue
        drv = mod.cells[mod.drivers[bit][0]]
        if drv.type in DFF_TYPES:
            found.add(mod.reg_of_bit.get(bit, mod.net(drv.conns["Q"][0])))
            continue
        stack += [b for p in _data_inputs(drv)
                  for b in drv.conns.get(p, [])]
    return found


def _flag_parallel_synchronizers(mod: Module, report: list,
                                 tree: dict) -> None:
    """Demote one-bit synchronizers that run in parallel across one boundary.

    Each chain is individually the right shape, which is why a purely
    structural rule accepts them. What makes a set of them wrong is that
    something reads them as one value: the bits resolve independently, so a
    reader can see a combination the sender never sent.

    Two rules, in that order of preference. The first finds a register that
    reads two chains together and names it, which is the specific finding a
    reader can act on. The second demotes any remaining set of chains that
    share a boundary -- same sending domain, same receiving domain -- even
    when nothing inside this netlist reads them together, because a value
    can leave through the module's ports and be reassembled by whatever
    instantiates it. That version of the design is the one the chapter's own
    exercise names, and the earlier rule accepted all eight bits of it: the
    convergence test was one register wide, so a bus that left the block
    never met a reader. The second rule can group two genuinely independent
    controls, which is why its note says the netlist does not settle the
    question rather than asserting a defect.
    """
    sync = [c for c in report if c["shape_recognized"]]
    if len(sync) < 2:
        return
    # A second-stage register can be shared: two bits of one declared
    # register are two second stages under one name. Keeping one crossing
    # per name lost the other, and a two-bit value on per-bit chains then
    # passed as two recognized shapes.
    stages = {}                       # second-stage register -> its crossings
    for c in sync:
        for n in c["second_stage"]:
            stages.setdefault(n, []).append(c)
    # Follow the whole chain, not one link of it. A three-flop synchronizer
    # puts a register between the second stage and whatever reads it, and a
    # rule that looked only at immediate readers saw nothing there.
    feeds = {n: _data_cone_registers(mod, c) for n, c in registers(mod)}

    def ancestors(name):
        """Every register upstream of this one, however far back.

        No memo. An earlier version cached while sharing one `seen` set down
        the recursion, so a nested call pruned nodes an outer call had
        already visited and then stored the pruned answer as if it were
        complete. The traversal order came from a Python set, so which
        answer got cached depended on the interpreter's hash seed.
        """
        out, stack = set(), [name]
        while stack:
            for p in feeds.get(stack.pop(), ()):
                if p not in out:
                    out.add(p)
                    stack.append(p)
        return out

    for name, cell in registers(mod):
        together = {id(c): c for n in ancestors(name) if n in stages
                    for c in stages[n]}
        if len(together) < 2:
            continue
        for c in together.values():
            c["shape_recognized"] = False
            c["note"] = (f"{len(together)} one-bit synchronizers are read "
                           f"together by {name}; their bits can resolve in "
                           f"different cycles")
    # The boundary is the pair of clock *nets*, not the pair of domain keys.
    # One clock gated two ways is two domain keys, so two chains off it were
    # two groups of one and neither rule fired: two bits of one value,
    # synchronized separately across one physical boundary, came back as two
    # recognized synchronizers. The roots are already in the clock tree,
    # which is how `same_clock_source` knows the same thing.
    def boundary(c):
        regs = tree["registers"]
        return (frozenset(regs.get(c["from"], {}).get("root_bits", [])),
                frozenset(regs.get(c["to"], {}).get("root_bits", [])))

    # A sender clocked by something the netlist cannot see into -- a
    # black-box clock buffer, say -- has an unknown relation to every other
    # sender into the same receiver, so it cannot be shown to cross a
    # different boundary from any of them. Its group is merged with theirs.
    cells = dict(registers(mod))
    opaque = {c["from"] for c in sync
              if any(s.kind == "unknown" for s in _walk_to_sources(
                  mod, cells[c["from"]].conns["CLK"][0], None, False, None))}
    groups = {}
    for c in sync:
        frm, to = boundary(c)
        groups.setdefault((frozenset() if c["from"] in opaque else frm, to),
                          []).append(c)
    for (frm, to), group in list(groups.items()):
        if not frm:
            for (f2, t2), other in groups.items():
                if t2 == to and f2:
                    group.extend(other)
                    other.clear()
    groups = {k: v for k, v in groups.items() if v}
    for group in groups.values():
        if len(group) < 2:
            continue
        frm = _pretty(group[0]["from_domain"])
        to = _pretty(group[0]["to_domain"])
        still = [c for c in group if c["shape_recognized"]]
        for c in still:
            c["shape_recognized"] = False
            c["note"] = (f"{len(group)} one-bit synchronizers cross from "
                           f"{frm} to {to} in parallel; if they carry one "
                           f"value its bits can resolve in different "
                           f"cycles, and the netlist does not say whether "
                           f"they do")


def unsure_pair(tree: dict, a: str, b: str) -> bool:
    """True if either end's clock could not be resolved."""
    regs = tree["registers"]
    return bool(regs.get(a, {}).get("clock_ambiguous")
                or regs.get(b, {}).get("clock_ambiguous"))


def _sources(tree: dict, name: str) -> set:
    """The clock source names the walk reached for one register."""
    return set(tree["registers"].get(name, {}).get("clock_sources", []))


def _feeds_directly(mod: Module, cell, source: str) -> bool:
    """True if `source` reaches this register's D with no logic in between
    *and* this register takes it on every clock.

    An enable makes this not a synchronizer stage: the value is held rather
    than resampled, so the second stage is not giving the first a full clock
    period to settle. Recognizing the enable matters because lowering a
    synchronous reset also lowers an enable onto its own pin, which moved
    the data onto D and made an enabled register look direct.
    """
    if any(b not in (0, "0") for b in cell.conns.get("EN", [])):
        return False
    # One hop, not a cone walk. "With no logic in between" is a statement
    # about the driver of this bit and nothing further back, and asking it
    # as a full backward walk made the run time grow with the square of a
    # lowered memory array: every call re-walked the whole read multiplexer.
    for b in cell.conns.get("D", []):
        drv = mod.drivers.get(b) if isinstance(b, int) else None
        if drv is None:
            continue
        c = mod.cells[drv[0]]
        if c.type in DFF_TYPES and source == mod.reg_of_bit.get(
                b, mod.net(c.conns["Q"][0])):
            return True
    return False


def _latch_crossings(mod: Module, dom_of: dict) -> list:
    """Crossings whose receiving element is a latch rather than a flip-flop.

    The walks pass *through* a latch in the middle of a path and record it,
    which is right. A latch at the end of one was never asked about at all,
    because the loop that asks only visits flip-flops: eight bits leaving one
    domain into a transparent latch held open by another domain's enable
    reported as a clean design. A latch has no clock, so the domain that
    decides when data is captured is the enable's, and that is what this
    compares against.
    """
    out = []
    for name, cell in mod.cells.items():
        if cell.type not in LATCH_TYPES:
            continue
        label = mod.reg_of_bit.get(cell.conns.get("Q", [None])[0]) \
            or mod.net(cell.conns["Q"][0]) if cell.conns.get("Q") else name
        enable = {dom_of[r] for b in cell.conns.get("EN", [])
                  for r in _cone_registers(mod, b) if r in dom_of}
        mine = (next(iter(enable)) if len(enable) == 1
                else f"undecided enable of {label}")
        # Every input except the enable, enumerated: a hand-written list
        # of data pins missed an asynchronous clear arriving from another
        # domain, which is a crossing whether or not it is on a data pin.
        data = {r for p in _data_inputs(cell) if p != "EN"
                for b in cell.conns.get(p, [])
                for r in _cone_registers(mod, b)}
        for src in sorted(data):
            theirs = dom_of.get(src, "unresolved clock")
            if theirs == mine:
                continue
            out.append({"to": label, "to_domain": mine, "from": src,
                        "from_domain": theirs,
                        "width": len(cell.conns.get("Q", [])),
                        "direct": False, "second_stage": [],
                        "shape_recognized": False,
                        "same_clock_source": False,
                        "note": "the receiving element is a latch, so its "
                                "enable decides when the data is captured "
                                "and a transition can be caught part-way",
                        "src": cell.src})
    return out


def _cone_registers(mod: Module, bit) -> set:
    """Registers reaching one net, through combinational logic and latches."""
    return {s.name for s in _walk_to_sources(mod, bit, None, True, None)
            if s.kind == "register"}


def crossings(mod: Module, tree: dict | None = None, declared=()) -> dict:
    """Registers that receive data from a register in another clock domain,
    and whether the receiving structure *matches a shape this tool knows*.

    The distinction is the whole design of this report, and it was learned
    the hard way. An earlier version answered "is this crossing safe", which
    is a judgment, and every defect it ever had was in making that
    judgment: a shape nobody had taught it was called safe, and once a rule
    meant to remove a false alarm silenced a real crossing entirely.

    So it answers a smaller question it can actually answer. `shape_recognized`
    is a fact about structure, not a verdict about correctness: true means
    the receiving path matches a two-flop synchronizer and is not one of
    several such paths carrying one value. A crossing whose shape is not
    recognized may be perfectly correct and merely unusual. Nothing is ever
    suppressed, and where the walk cannot resolve a clock it says so. Whether
    a crossing is *safe* is a question about the specification, and
    @sec-ch03-cdc is where a person answers it."""
    tree = tree or clock_tree(mod, declared)
    dom_of = {r: i["domain"] for r, i in tree["registers"].items()}
    by_name = {name: cell for name, cell in registers(mod)}
    # Who is fed directly by whom, computed once. Asking `_feeds_directly`
    # for every (sender, receiver) pair made the second-stage scan
    # quadratic in the register count -- sixty-seven million calls on an
    # eight-thousand-row array.
    fed_by = {}
    for rname, rcell in by_name.items():
        if any(b not in (0, "0") for b in rcell.conns.get("EN", [])):
            continue
        for b in rcell.conns.get("D", []):
            drv = mod.drivers.get(b) if isinstance(b, int) else None
            if drv and mod.cells[drv[0]].type in DFF_TYPES:
                src_cell = mod.cells[drv[0]]
                src = mod.reg_of_bit.get(b, mod.net(src_cell.conns["Q"][0]))
                fed_by.setdefault(src, set()).add(rname)
    report = []
    for name, cell in by_name.items():
        mine = dom_of[name]
        for src in _data_cone_registers(mod, cell):
            # An unresolvable clock is exactly what a verifier needs to see,
            # so it gets its own domain name rather than the destination's.
            # One spelling, used everywhere below: an earlier version read
            # `dom_of[src]` four lines later, so either the default here was
            # unreachable or the report raised on the case it described.
            theirs = dom_of.get(src, "unresolved clock")
            if theirs == mine:
                continue
            # An earlier version suppressed a crossing whenever the two
            # domain names shared a token, meaning to say "one clock, gated
            # two ways". Domain names carry gating control when the walk
            # could not tell a clock from an enable, so two genuinely
            # asynchronous clocks sharing one global enable were silenced --
            # a real crossing reported as a clean design. Nothing is
            # suppressed here now. Where the walk could not decide, the
            # crossing is reported *as* undecided, below, so the failure is
            # loud rather than silent.
            # direct connection (no logic) from src to this register's D?
            direct = _feeds_directly(mod, cell, src)
            # Does another register in this domain take it straight from
            # here, on the same clock edge? A second stage on the opposite
            # edge gives the first only half a period to settle, which is
            # not what @sec-ch03-cdc means by a synchronizer.
            edge = cell.params.get("CLK_POLARITY")
            second_stage = sorted(
                n for n in fed_by.get(name, ())
                if dom_of[n] == mine and n != name
                and by_name[n].params.get("CLK_POLARITY") == edge)
            # Two clock nets that resolve to *one* source are one clock,
            # gated differently. That is a timing question, not a
            # metastability one, and it does not trip the gate, because
            # every gated design would otherwise fail. The test is a single
            # shared root, not an equal set of them: two multiplexers over
            # the same pair of asynchronous clocks reach an equal set and
            # are not one clock, and comparing sets marked exactly that case
            # safe. Reporting is unaffected either way; nothing is dropped.
            mine_roots = set(tree["registers"].get(name, {})
                             .get("root_bits", []))
            their_roots = set(tree["registers"].get(src, {})
                              .get("root_bits", []))
            # The excuse requires a declaration. It is the only route by
            # which a reported crossing stops failing the run, and without a
            # declaration it rests on a guess about which input of a gate
            # was the clock -- a guess five different netlist shapes have
            # now been shown to defeat. Undeclared, a gated design fails and
            # says to declare the clocks; that is the feature earning its
            # place rather than only ever removing findings.
            same_source = (bool(declared)
                           and not unsure_pair(tree, name, src)
                           and len(mine_roots) == 1
                           and mine_roots == their_roots)
            width = len(cell.conns.get("Q", []))
            unsure = unsure_pair(tree, name, src)
            synchronizer = (direct and bool(second_stage)
                            and width == 1 and not unsure)
            report.append({"to": name, "to_domain": mine, "from": src,
                           "from_domain": theirs, "width": width,
                           "direct": direct, "second_stage": second_stage,
                           "shape_recognized": synchronizer,
                           "same_clock_source": same_source,
                           "note": ("" if synchronizer else
                                      ("clock and enable not distinguishable "
                                       + ("from the netlist" if declared else
                                          "here; declare the clocks"))
                                      if unsure
                                      else "no synchronizer shape"),
                           "src": cell.src})
    report += _latch_crossings(mod, dom_of)
    _flag_parallel_synchronizers(mod, report, tree)
    # collapse: a crossing that lands on a synchronizer's first stage is fine;
    # flag the rest
    # The gate trips on a shape it does not know between two different
    # clock sources. A same-source pair stays in `crossings`, where a reader
    # sees it, and out of the list a build fails on.
    unrecognized = [c for c in report
                    if not c["shape_recognized"] and not c["same_clock_source"]]
    return {"crossings": report, "unrecognized": unrecognized}
