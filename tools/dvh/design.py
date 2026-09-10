"""design.py -- load an elaborated design as a graph the other tools can walk.

Two views of the same RTL:

  * ``load_flat(files, top)``   a flattened netlist from Yosys, for walking
                                clocks, resets and data cones across the
                                whole design; registers are named by the net
                                on their Q output, e.g. ``u_dp.count``.
  * ``load_hier(files, top)``   the hierarchical netlist, for the instance
                                connection graph.

Both come from ``yosys -p "... write_json"``; this module only parses the
JSON. Yosys must be on PATH. Nothing here needs a simulator.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field

# Sequential cell types Yosys produces after the passes below (no
# technology mapping).
DFF_TYPES = {
    "$dff", "$dffe", "$adff", "$adffe", "$sdff", "$sdffe", "$sdffce",
    "$aldff", "$aldffe", "$dffsr", "$dffsre",
}
ASYNC_RESET_TYPES = {"$adff", "$adffe", "$aldff", "$aldffe",
                     "$dffsr", "$dffsre"}
SYNC_RESET_TYPES = {"$sdff", "$sdffe", "$sdffce"}


@dataclass
class Cell:
    name: str
    type: str
    params: dict
    conns: dict          # port name -> list of bit ids (int) or const strings
    dirs: dict           # port name -> "input" | "output"
    src: str = ""        # "file:line.col-line.col", from Yosys's src attribute


@dataclass
class Module:
    name: str
    ports: dict          # port name -> {"direction": ..., "bits": [...]}
    cells: dict          # cell name -> Cell
    netnames: dict       # net name -> {"bits": [...], "hide_name": 0/1}
    bit_names: dict = field(default_factory=dict)   # bit id -> best net name
    drivers: dict = field(default_factory=dict)    # bit id -> (cell, port)
    port_of_bit: dict = field(default_factory=dict)  # bit id -> input port
    reg_of_bit: dict = field(default_factory=dict)   # Q bit -> register name

    def finish(self):
        for name, net in self.netnames.items():
            hidden = net.get("hide_name", 0)
            for b in net["bits"]:
                if not isinstance(b, int):
                    continue
                known = self.bit_names.get(b)
                # A named net always wins over a generated one like $abc$123.
                if known is None or (not hidden and known.startswith("$")):
                    self.bit_names[b] = name
        for cname, cell in self.cells.items():
            for port, bits in cell.conns.items():
                if cell.dirs.get(port) == "output":
                    for b in bits:
                        if isinstance(b, int):
                            self.drivers[b] = (cname, port)
        for pname, p in self.ports.items():
            if p["direction"] == "input":
                for b in p["bits"]:
                    if isinstance(b, int):
                        self.port_of_bit[b] = pname

    def net(self, bit) -> str:
        if not isinstance(bit, int):
            return f"const {bit}"
        return self.bit_names.get(bit, f"bit{bit}")


def _run_yosys(files, top, flatten: bool) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "design.json")
        reads = " ".join(f"read_verilog -sv {f};" for f in files)
        # `proc` alone is not enough twice over. It leaves a synchronous
        # reset as a multiplexer in front of a plain flip-flop, so without
        # `opt_dff` every synchronously reset register is reported as having
        # no reset. And it leaves an array as memory cells rather than
        # registers, so without the memory passes a value crossing clock
        # domains through a RAM is invisible: the write port is not a
        # register, its clock is not a domain, and the read port stops the
        # data walk.
        script = (f"{reads} hierarchy -check -top {top}; proc; opt_dff; "
                  "memory_collect; memory_map; ")
        if flatten:
            script += "flatten; "
        script += f"opt_clean; write_json {out}"
        subprocess.run(["yosys", "-q", "-p", script], check=True,
                       capture_output=True, text=True)
        with open(out) as f:
            return json.load(f)


def _relative(src: str) -> str:
    """Yosys reports an absolute path; a report is more useful, and more
    reproducible between machines, with a path relative to where it ran."""
    if not src:
        return ""
    out = []
    for part in src.split("|"):          # Yosys joins several with '|'
        file, _, span = part.partition(":")
        try:
            file = os.path.relpath(file)
        except ValueError:               # different drive on Windows
            pass
        out.append(f"{file}:{span}" if span else file)
    return "|".join(out)


def _parse(data: dict) -> dict:
    mods = {}
    for mname, m in data["modules"].items():
        cells = {}
        for cname, c in m.get("cells", {}).items():
            attrs = c.get("attributes", {})
            cells[cname] = Cell(cname, c["type"], c.get("parameters", {}),
                                c.get("connections", {}),
                                c.get("port_directions", {}),
                                _relative(attrs.get("src", "")))
        mod = Module(mname, m.get("ports", {}), cells, m.get("netnames", {}))
        mod.finish()
        # One naming for registers, shared by every walk: a bit-blasted
        # register must resolve to the same name registers() yields for it.
        mod.reg_of_bit = {b: name for name, cell in registers(mod)
                          for b in cell.conns.get("Q", [])
                          if isinstance(b, int)}
        mods[mname] = mod
    return mods


def load_flat(files, top) -> Module:
    """The flattened top module, for clock, reset and cone walks."""
    return _parse(_run_yosys(files, top, flatten=True))[top]


def load_hier(files, top) -> dict:
    """All modules, hierarchy kept, for the connection graph."""
    return _parse(_run_yosys(files, top, flatten=False))


def registers(mod: Module):
    """Yield (register name, Cell) for every flip-flop, named by its Q net.

    Yosys may bit-blast one declared register into several one-bit cells
    driving the same net. Naming them all after the net would collide, and a
    caller building a dict would silently keep only the last, so a net with
    more than one register on it has the bit position appended.
    """
    pos = {}                       # bit id -> its index within its own net
    for net in mod.netnames.values():
        for i, b in enumerate(net["bits"]):
            if isinstance(b, int):
                pos.setdefault(b, i)
    cells = [(c, cell) for c, cell in mod.cells.items()
             if cell.type in DFF_TYPES]
    shared = {}
    for cname, cell in cells:
        q = cell.conns.get("Q", [])
        shared[mod.net(q[0]) if q else cname] = \
            shared.get(mod.net(q[0]) if q else cname, 0) + 1
    used = set()
    for cname, cell in cells:
        q = cell.conns.get("Q", [])
        base = mod.net(q[0]) if q else cname
        name = base if shared[base] == 1 else f"{base}[{pos.get(q[0], 0)}]"
        while name in used:        # last resort: never drop a register
            name += "'"
        used.add(name)
        yield name, cell
