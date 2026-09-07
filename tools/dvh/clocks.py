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

# Latches are state elements, not combinational logic. Walking through one
# would hide a crossing that lands on it, so both walks stop here instead.
LATCH_TYPES = {"$dlatch", "$adlatch", "$dlatchsr", "$sr",
               "$_DLATCH_P_", "$_DLATCH_N_", "$_SR_PP_", "$_SR_NN_"}

MUX_TYPES = ("$mux", "$pmux", "$_MUX_")


@dataclass
class Source:
    name: str            # port name or register name
    kind: str            # "port" | "register" | "constant" | "unknown"
    through: list = field(default_factory=list)   # cell types walked through


def primary_clocks(mod: Module) -> set:
    """Ports that drive a register's clock pin with no logic in between.

    These anchor the clock walk: at a gate or a multiplexer, an input whose
    cone reaches one of these is carrying the clock, and the rest are
    control."""
    prim = set()
    for _, cell in registers(mod):
        bits = cell.conns.get("CLK", [])
        if bits and isinstance(bits[0], int) and bits[0] in mod.port_of_bit:
            prim.add(mod.port_of_bit[bits[0]])
    return prim


def _reaches(mod: Module, bit, roots, any_comb) -> bool:
    """Does this net's cone reach one of the primary clocks?"""
    return any(s.name in roots
               for s in _walk_to_sources(mod, bit, set(), any_comb, None))


def _walk_to_sources(mod: Module, bit, seen=None, any_comb=False,
                     clock_roots=None) -> list[Source]:
    """All sources reachable backwards from `bit` through combinational logic.

    With any_comb=True every combinational cell is walked (data cones);
    otherwise only the clock-tree pass-through set is (clock and reset nets).
    With clock_roots given, a gate or multiplexer follows only the inputs
    whose cone reaches a primary clock, so a clock gate's enable does not
    become part of the domain name."""
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
    if cell.type in LATCH_TYPES:
        return [Source(mod.net(bit), "latch")]
    combinational = (cell.type not in DFF_TYPES
                     and cell.type not in LATCH_TYPES
                     and not cell.type.startswith("$mem"))
    if cell.type in PASS_THROUGH or (any_comb and combinational):
        # A multiplexer's select is not a clock, so the clock walk skips it.
        # A data cone must follow it: a foreign register steering a mux is a
        # crossing like any other.
        skip_select = not any_comb and cell.type in MUX_TYPES
        ins = [(port, b) for port, bits in cell.conns.items()
               if cell.dirs.get(port) == "input"
               and not (skip_select and port == "S")
               for b in bits]
        control = []
        if clock_roots:
            carrying = [(p, b) for (p, b) in ins
                        if _reaches(mod, b, clock_roots, any_comb)]
            if carrying:        # else nothing here is a clock: keep them all
                control = [mod.net(b) for (p, b) in ins
                           if (p, b) not in carrying]
                ins = carrying
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
        return out
    return [Source(f"{mod.net(bit)} (driven by {cell.type})", "unknown")]


def clock_tree(mod: Module) -> dict:
    """Registers grouped by clock source; each register with its clock path."""
    regs = {}
    prim = primary_clocks(mod)
    for name, cell in registers(mod):
        srcs = _walk_to_sources(mod, cell.conns["CLK"][0], None, False, prim)
        roots = sorted({s.name for s in srcs})
        gated = any(s.through for s in srcs)
        regs[name] = {"clock_sources": roots, "gated_or_muxed": gated,
                      "through": sorted({t for s in srcs for t in s.through})}
    domains = {}
    for name, info in regs.items():
        key = "+".join(info["clock_sources"])
        domains.setdefault(key, []).append(name)
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
            none.append(name)
            continue
        prim = primary_clocks(mod)
        srcs = []
        for b in cell.conns[pin]:      # $dffsr's set/reset are per-bit vectors
            srcs += _walk_to_sources(mod, b, None, False, prim)
        out[name] = {"kind": kind,
                     "active": "high" if str(pol).endswith("1") else "low",
                     "sources": sorted({s.name for s in srcs}),
                     "through": sorted({t for s in srcs for t in s.through})}
    return {"registers": out, "no_reset": sorted(none)}


def _data_cone_registers(mod: Module, cell) -> set[str]:
    """Registers feeding this register's D (and EN) inputs, through logic."""
    found = set()
    for port in ("D", "EN"):
        for b in cell.conns.get(port, []):
            for s in _walk_to_sources(mod, b, None, True, None):
                if s.kind == "register":
                    found.add(s.name)
    return found


def _value_of(register_name: str) -> str:
    """The declared value a register belongs to, without its bit index."""
    return register_name.split("[")[0]


def _flag_parallel_synchronizers(report: list) -> None:
    """Demote a set of one-bit synchronizers carrying one multi-bit value.

    Each chain is individually the right shape, which is why a purely
    structural rule accepts them, and together they are the loss of data
    that a multi-bit crossing must not be. The bits are resynchronized
    independently, so they are not guaranteed to arrive in the same cycle.
    """
    groups = {}
    for c in report:
        if c["synchronized"]:
            key = (_value_of(c["from"]), c["to_domain"])
            groups.setdefault(key, []).append(c)
    for (value, _), members in groups.items():
        if len(members) > 1:
            for c in members:
                c["synchronized"] = False
                c["reason"] = (f"{len(members)} parallel one-bit "
                               f"synchronizers on {value}; the bits may "
                               f"arrive in different cycles")


def _feeds_directly(mod: Module, cell, source: str) -> bool:
    """True if `source` reaches this register's D with no logic in between.
    That is the shape a synchronizer's first stage has, and the shape any
    correct crossing structure starts with."""
    return any(s.kind == "register" and s.name == source and not s.through
               for b in cell.conns.get("D", [])
               for s in _walk_to_sources(mod, b, None, True, None))


def crossings(mod: Module, tree: dict | None = None) -> dict:
    """Registers that receive data from a register in another clock domain,
    and whether the receiving path looks like a synchronizer (a register
    whose D is fed directly, with no logic, by the foreign register, and
    which itself feeds another register in the same domain the same way)."""
    tree = tree or clock_tree(mod)
    dom_of = {r: "+".join(i["clock_sources"])
              for r, i in tree["registers"].items()}
    by_name = {name: cell for name, cell in registers(mod)}
    report = []
    for name, cell in by_name.items():
        mine = dom_of[name]
        for src in _data_cone_registers(mod, cell):
            # An unresolvable clock is exactly what a verifier needs to see,
            # so it gets its own domain name rather than the destination's.
            if dom_of.get(src, "unresolved clock") == mine:
                continue
            # direct connection (no logic) from src to this register's D?
            direct = _feeds_directly(mod, cell, src)
            # does another register in this domain take it straight from here?
            second_stage = [n for n, c in by_name.items()
                            if dom_of[n] == mine and n != name
                            and _feeds_directly(mod, c, name)]
            width = len(cell.conns.get("Q", []))
            synchronizer = direct and bool(second_stage) and width == 1
            report.append({"to": name, "to_domain": mine, "from": src,
                           "from_domain": dom_of[src], "width": width,
                           "direct": direct, "second_stage": second_stage,
                           "synchronized": synchronizer,
                           "reason": "" if synchronizer else "no synchronizer"})
    _flag_parallel_synchronizers(report)
    # collapse: a crossing that lands on a synchronizer's first stage is fine;
    # flag the rest
    flagged = [c for c in report if not c["synchronized"]]
    return {"crossings": report, "unsynchronized": flagged}
