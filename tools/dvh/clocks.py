"""clocks.py -- clock tree, reset tree and crossing report from a flattened
netlist (see design.py).

The walks follow a net backwards from a register's clock (or reset) pin to
its source. A source is a top-level input port or a register output (a
divided or generated clock). Buffers, inverters, gates and multiplexers are
walked through and recorded.

A clock walk has to tell a gate's clock input from its enable, or every
gated register lands in a domain of its own and an ordinary synchronous path
across a clock gate is reported as a crossing. It does that by first finding
the primary clocks -- ports that drive some register's clock pin with no
logic in between -- and then, at each gate, following only the inputs whose
cone reaches one of them. The other inputs are gating control, and are
recorded in `through` rather than in the domain name.
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
    through: list = field(default_factory=list)   # cell types walked through


def clock_candidates(mod: Module) -> tuple:
    """Two tiers of evidence that a net is carrying a clock, not control.

    At a gate feeding a clock pin, one input is the clock and the others are
    enables, and nothing in the netlist says which. Two signals separate them
    most of the time. **Strong**: the net already drives some register's
    clock pin directly, or is a register output used as a clock (a divider),
    or is something the netlist cannot see into, which is what an analog
    block looks like from here. **Weak**: it is an input port, which a clock
    usually is and an enable sometimes is.

    Where the strong evidence is absent and more than one input is merely a
    port, the two are genuinely indistinguishable from the RTL, and the walk
    says so rather than guessing. That is not a defect in the tool; it is
    @sec-ch03-clocks' point that the relationship between clocks is a
    property of the specification. Pass the clock names in and the question
    does not arise.
    """
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


def _tier(mod: Module, bit, strong, weak, any_comb) -> int:
    """2 for strong evidence of a clock, 1 for weak, 0 for none."""
    srcs = _walk_to_sources(mod, bit, set(), any_comb, None)
    if any(s.name in strong or s.kind == "unknown" for s in srcs):
        return 2
    return 1 if any(s.name in weak for s in srcs) else 0


def _walk_to_sources(mod: Module, bit, seen=None, any_comb=False,
                     clock_roots=None) -> list[Source]:
    """All sources reachable backwards from `bit` through combinational logic.

    With any_comb=True every combinational cell is walked (data cones);
    otherwise only the clock-tree pass-through set is (clock and reset nets).
    `clock_roots` is the (strong, weak) pair from `clock_candidates`, or a
    single set of declared clock names; a gate then follows only the inputs
    that look like clocks, so an enable does not join the domain name."""
    seen = seen if seen is not None else set()
    if not isinstance(bit, int):
        return [Source(f"const {bit}", "constant")]
    if bit in seen:
        return []
    seen.add(bit)
    if bit in mod.port_of_bit:
        return [Source(mod.port_of_bit[bit], "port")]
    drv = mod.drivers.get(bit)
    if drv is None:
        return [Source(mod.net(bit), "unknown")]
    cell = mod.cells[drv[0]]
    if cell.type in DFF_TYPES:
        return [Source(mod.reg_of_bit.get(bit, mod.net(cell.conns["Q"][0])),
                       "register")]
    combinational = (cell.type not in DFF_TYPES
                     and not cell.type.startswith("$mem"))
    if cell.type in LATCH_TYPES and any_comb:
        # A latch is a state element, so a path through one is not direct and
        # cannot be a synchronizer; but the crossing behind it is still a
        # crossing, so the walk continues rather than stopping here.
        out = []
        for b in cell.conns.get("D", []):
            for src in _walk_to_sources(mod, b, seen, any_comb, clock_roots):
                src.through = [cell.type] + src.through
                out.append(src)
        return out or [Source(mod.net(bit), "latch")]
    if cell.type in LATCH_TYPES:
        return [Source(mod.net(bit), "latch")]
    if cell.type in PASS_THROUGH or (any_comb and combinational):
        # A multiplexer's select is not a clock, so the clock walk skips it.
        # A data cone must follow it: a foreign register steering a mux is a
        # crossing like any other.
        skip_select = not any_comb and cell.type in MUX_TYPES
        ins = [(port, b) for port, bits in cell.conns.items()
               if cell.dirs.get(port) == "input"
               and not (skip_select and port == "S")
               for b in bits]
        control, ambiguous = [], False
        if clock_roots:
            strong, weak = clock_roots
            tiers = [(_tier(mod, b, strong, weak, any_comb), p, b)
                     for (p, b) in ins]
            best = max((t for t, _, _ in tiers), default=0)
            carrying = [(p, b) for (t, p, b) in tiers if t == best]
            if best and len(carrying) < len(ins):
                control = [mod.net(b) for (p, b) in ins
                           if (p, b) not in carrying]
                ins = carrying
            elif best == 1 and len(carrying) > 1:
                # Several ports and no stronger evidence: from the RTL alone
                # these are indistinguishable. Say so instead of choosing.
                ambiguous = True
        out = []
        for port, b in ins:
            for s in _walk_to_sources(mod, b, seen, any_comb, clock_roots):
                s.through = [cell.type] + s.through
                out.append(s)
        if cell.type in MUX_TYPES:
            for s in out:
                s.through = ["mux"] + s.through
        for s in out:           # name the gating control we did not follow
            s.through += [f"gated by {c}" for c in sorted(set(control))]
            if ambiguous:
                s.through += ["ambiguous: clock not distinguishable here"]
        return out
    return [Source(f"{mod.net(bit)} (driven by {cell.type})", "unknown")]


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


def clock_tree(mod: Module) -> dict:
    """Registers grouped by clock source; each register with its clock path."""
    regs = {}
    prim = clock_candidates(mod)
    for name, cell in registers(mod):
        srcs = _walk_to_sources(mod, cell.conns["CLK"][0], None, False, prim)
        roots = sorted({s.name for s in srcs})
        gated = any(s.through for s in srcs)
        through = sorted({t for s in srcs for t in s.through})
        unsure = any(t.startswith("ambiguous") for t in through)
        regs[name] = {"clock_sources": roots, "gated_or_muxed": gated,
                      "through": through, "src": cell.src,
                      "clock_ambiguous": unsure,
                      "domain": _domain_key(mod, cell, srcs, unsure, name)}
    domains = {}
    for name, info in regs.items():
        domains.setdefault(info["domain"], []).append(name)
    return {"domains": {k: sorted(v) for k, v in domains.items()},
            "registers": regs}


def reset_tree(mod: Module) -> dict:
    """Every register's reset: kind, polarity, source; and the ones without."""
    out, none = {}, []
    for name, cell in registers(mod):
        if cell.type in ASYNC_RESET_TYPES:
            pin = "ARST" if "ARST" in cell.conns else "CLR"
            pol = cell.params.get("ARST_POLARITY",
                                  cell.params.get("CLR_POLARITY", "1"))
            kind = "asynchronous"
        elif cell.type in SYNC_RESET_TYPES:
            pin, kind = "SRST", "synchronous"
            pol = cell.params.get("SRST_POLARITY", "1")
        else:
            # The unreset registers are the finding a reader acts on, so
            # they carry a location like every other finding.
            none.append({"name": name, "src": cell.src})
            continue
        prim = clock_candidates(mod)
        srcs = []
        for b in cell.conns[pin]:      # $dffsr's set/reset are per-bit vectors
            srcs += _walk_to_sources(mod, b, None, False, prim)
        out[name] = {"kind": kind,
                     "active": "high" if str(pol).endswith("1") else "low",
                     "sources": sorted({s.name for s in srcs}),
                     "through": sorted({t for s in srcs for t in s.through}),
                     "src": cell.src}
    return {"registers": out,
            "no_reset": sorted(none, key=lambda r: r["name"])}


def _data_cone_registers(mod: Module, cell) -> set[str]:
    """Registers feeding this register's D (and EN) inputs, through logic."""
    found = set()
    for port in ("D", "EN"):
        for b in cell.conns.get(port, []):
            for s in _walk_to_sources(mod, b, None, True, None):
                if s.kind == "register":
                    found.add(s.name)
    return found


def _flag_converging_synchronizers(mod: Module, report: list) -> None:
    """Demote one-bit synchronizers that are read together.

    Each chain is individually the right shape, which is why a purely
    structural rule accepts them. What makes a set of them wrong is that
    something downstream reads them as one value: the bits resolve
    independently, so a reader can see a combination the sender never sent.

    Convergence is the signal, not the sending register's name. Grouping by
    name would miss a value carried on eight separately declared flops and
    would wrongly flag two unrelated controls that happen to share one
    declared vector.
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
    reach = {}

    def ancestors(name, seen=None):
        seen = seen if seen is not None else set()
        if name in reach:
            return reach[name]
        out = set()
        for p in feeds.get(name, ()):  # noqa: PLR1704
            if p in seen:
                continue
            seen.add(p)
            out.add(p)
            out |= ancestors(p, seen)
        reach[name] = out
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
    return any(s.kind == "register" and s.name == source and not s.through
               for b in cell.conns.get("D", [])
               for s in _walk_to_sources(mod, b, None, True, None))


def crossings(mod: Module, tree: dict | None = None) -> dict:
    """Registers that receive data from a register in another clock domain,
    and whether the receiving structure *matches a shape this tool knows*.

    The distinction is the whole design of this report, and it was learned
    the hard way. An earlier version answered "is this crossing safe", which
    is a judgement, and every defect it ever had was in making that
    judgement: a shape nobody had taught it was called safe, and once a rule
    meant to remove a false alarm silenced a real crossing entirely.

    So it answers a smaller question it can actually answer. `shape_recognized`
    is a fact about structure, not a verdict about correctness: true means
    the receiving path matches a two-flop synchronizer and is not one of
    several such paths carrying one value. A crossing whose shape is not
    recognized may be perfectly correct and merely unusual. Nothing is ever
    suppressed, and where the walk cannot resolve a clock it says so. Whether
    a crossing is *safe* is a question about the specification, and
    @sec-ch03-cdc is where a person answers it."""
    tree = tree or clock_tree(mod)
    dom_of = {r: i["domain"] for r, i in tree["registers"].items()}
    by_name = {name: cell for name, cell in registers(mod)}
    report = []
    for name, cell in by_name.items():
        mine = dom_of[name]
        for src in _data_cone_registers(mod, cell):
            # An unresolvable clock is exactly what a verifier needs to see,
            # so it gets its own domain name rather than the destination's.
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
            # does another register in this domain take it straight from here?
            second_stage = [n for n, c in by_name.items()
                            if dom_of[n] == mine and n != name
                            and _feeds_directly(mod, c, name)]
            # Two clock nets that resolve to *one* source are one clock,
            # gated differently. That is a timing question, not a
            # metastability one, and it does not trip the gate, because
            # every gated design would otherwise fail. The test is a single
            # shared root, not an equal set of them: two multiplexers over
            # the same pair of asynchronous clocks reach an equal set and
            # are not one clock, and comparing sets marked exactly that case
            # safe. Reporting is unaffected either way; nothing is dropped.
            roots = _sources(tree, name)
            same_source = (not unsure_pair(tree, name, src)
                           and len(roots) == 1
                           and roots == _sources(tree, src))
            width = len(cell.conns.get("Q", []))
            unsure = unsure_pair(tree, name, src)
            synchronizer = (direct and bool(second_stage)
                            and width == 1 and not unsure)
            report.append({"to": name, "to_domain": mine, "from": src,
                           "from_domain": dom_of[src], "width": width,
                           "direct": direct, "second_stage": second_stage,
                           "shape_recognized": synchronizer,
                           "same_clock_source": same_source,
                           "note": ("" if synchronizer else
                                      "clock and enable not distinguishable "
                                      "here; declare the clocks" if unsure
                                      else "no synchronizer shape"),
                           "src": cell.src})
    _flag_converging_synchronizers(mod, report)
    # collapse: a crossing that lands on a synchronizer's first stage is fine;
    # flag the rest
    # The gate trips on a shape it does not know between two different
    # clock sources. A same-source pair stays in `crossings`, where a reader
    # sees it, and out of the list a build fails on.
    unrecognized = [c for c in report
                    if not c["shape_recognized"] and not c["same_clock_source"]]
    return {"crossings": report, "unrecognized": unrecognized}
