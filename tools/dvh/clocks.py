"""clocks.py -- clock tree, reset tree and crossing report from a flattened
netlist (see design.py).

The walks follow a net backwards from a register's clock (or reset) pin to
its source. A source is a top-level input port or a register output (a
divided or generated clock). Buffers, inverters, gates and multiplexers are
walked through and recorded, so a gated or muxed clock is reported with its
gating logic rather than treated as a new domain.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .design import (ASYNC_RESET_TYPES, DFF_TYPES, SYNC_RESET_TYPES,
                     Module, registers)

# Combinational cell types the walks pass through.
PASS_THROUGH = {"$not", "$and", "$or", "$xor", "$mux", "$pmux", "$logic_not",
                "$logic_and", "$logic_or", "$_BUF_", "$_NOT_", "$_AND_",
                "$_OR_", "$_MUX_", "$reduce_or", "$reduce_and", "$eq", "$ne"}


@dataclass
class Source:
    name: str            # port name or register name
    kind: str            # "port" | "register" | "constant" | "unknown"
    through: list = field(default_factory=list)   # cell types walked through


def _walk_to_sources(mod: Module, bit, seen=None,
                     any_comb=False) -> list[Source]:
    """All sources reachable backwards from `bit` through combinational logic.
    With any_comb=True every non-register cell is walked through (data cones);
    otherwise only the clock-tree pass-through set is (clock and reset nets)."""
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
        return [Source(mod.net(cell.conns["Q"][0]), "register")]
    combinational = (cell.type not in DFF_TYPES
                     and not cell.type.startswith("$mem"))
    if cell.type in PASS_THROUGH or (any_comb and combinational):
        out = []
        for port, bits in cell.conns.items():
            if cell.dirs.get(port) == "input" and port not in ("S",):
                for b in bits:
                    for s in _walk_to_sources(mod, b, seen, any_comb):
                        s.through = [cell.type] + s.through
                        out.append(s)
        # a mux's select is not a clock source, but note it
        if cell.type in ("$mux", "$pmux", "$_MUX_"):
            for s in out:
                s.through = ["mux"] + s.through
        return out
    return [Source(f"{mod.net(bit)} (driven by {cell.type})", "unknown")]


def clock_tree(mod: Module) -> dict:
    """Registers grouped by clock source; each register with its clock path."""
    regs = {}
    for name, cell in registers(mod):
        srcs = _walk_to_sources(mod, cell.conns["CLK"][0])
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
        srcs = _walk_to_sources(mod, cell.conns[pin][0])
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
            for s in _walk_to_sources(mod, b, any_comb=True):
                if s.kind == "register":
                    found.add(s.name)
    return found


def _feeds_directly(mod: Module, cell, source: str) -> bool:
    """True if `source` reaches this register's D with no logic in between.
    That is the shape a synchronizer's first stage has, and the shape any
    correct crossing structure starts with."""
    return any(s.kind == "register" and s.name == source and not s.through
               for b in cell.conns.get("D", [])
               for s in _walk_to_sources(mod, b, any_comb=True))


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
            if dom_of.get(src, mine) == mine:
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
                           "synchronized": synchronizer})
    # collapse: a crossing that lands on a synchronizer's first stage is fine;
    # flag the rest
    flagged = [c for c in report if not c["synchronized"]]
    return {"crossings": report, "unsynchronized": flagged}
