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

# Sequential cell types Yosys produces after `proc` (no technology mapping).
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


@dataclass
class Module:
    name: str
    ports: dict          # port name -> {"direction": ..., "bits": [...]}
    cells: dict          # cell name -> Cell
    netnames: dict       # net name -> {"bits": [...], "hide_name": 0/1}
    bit_names: dict = field(default_factory=dict)   # bit id -> best net name
    drivers: dict = field(default_factory=dict)    # bit id -> (cell, port)
    port_of_bit: dict = field(default_factory=dict)  # bit id -> input port name

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
        script = f"{reads} hierarchy -check -top {top}; proc; "
        if flatten:
            script += "flatten; "
        script += f"opt_clean; write_json {out}"
        subprocess.run(["yosys", "-q", "-p", script], check=True,
                       capture_output=True, text=True)
        with open(out) as f:
            return json.load(f)


def _parse(data: dict) -> dict:
    mods = {}
    for mname, m in data["modules"].items():
        cells = {}
        for cname, c in m.get("cells", {}).items():
            cells[cname] = Cell(cname, c["type"], c.get("parameters", {}),
                                c.get("connections", {}),
                                c.get("port_directions", {}))
        mod = Module(mname, m.get("ports", {}), cells, m.get("netnames", {}))
        mod.finish()
        mods[mname] = mod
    return mods


def load_flat(files, top) -> Module:
    """The flattened top module, for clock, reset and cone walks."""
    return _parse(_run_yosys(files, top, flatten=True))[top]


def load_hier(files, top) -> dict:
    """All modules, hierarchy kept, for the connection graph."""
    return _parse(_run_yosys(files, top, flatten=False))


def registers(mod: Module):
    """Yield (register name, Cell) for every flip-flop, named by its Q net."""
    for cname, cell in mod.cells.items():
        if cell.type in DFF_TYPES:
            q = cell.conns.get("Q", [])
            name = mod.net(q[0]) if q else cname
            yield name, cell
