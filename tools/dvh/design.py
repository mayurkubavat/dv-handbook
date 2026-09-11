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
import re
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


class DesignError(Exception):
    """The design could not be read. Not a finding about the design."""


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
    src: str = ""        # the module declaration, the last resort location
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
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        raise DesignError(f"no such file: {', '.join(missing)}")
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
        # A second dump, taken before the memory passes run. `memory_map`
        # synthesizes the registers an array becomes and gives them no
        # attributes, so the only record of where that array was declared is
        # on the `$mem_v2` cell that exists only in this earlier picture.
        # Without it a lowered register had to borrow a location from a net
        # it touched, and what it borrowed was the line the *clock port* was
        # declared on -- a location that is well formed, passes every
        # schema, and sends a reader to the wrong place.
        # The earlier picture is flattened when the final one is, so a
        # memory is keyed by the same instance path the registers it becomes
        # will carry. Without that, two modules each declaring an array
        # called `mem` -- ordinary RTL -- were one ambiguous key, the
        # location was dropped as unsafe to guess, and the registers fell
        # through to the *top* module's declaration: a location in a
        # different module from the array it claims to name.
        mem = os.path.join(tmp, "memories.json")
        script = (f"{reads} hierarchy -check -top {top}; proc; opt_dff; "
                  "memory_collect; design -save premap; ")
        # `flatten` honors `keep_hierarchy`, and a submodule carrying it is
        # left as an instance: every register inside it is in a module the
        # walks never look at, so a design whose crossing lives in a kept
        # block reported no clocks, no registers and no crossings, and the
        # gate passed. The attribute is a synthesis instruction and has no
        # bearing on what the design does, so it is removed first.
        # Both forms: `-mod` reaches a module's attribute and the bare form
        # reaches a cell's, and `flatten` honors either. Stripping only the
        # module form turned the ordinary way of keeping one instance out of
        # a flatten into a tool that could not answer at all.
        unkeep = ("setattr -mod -unset keep_hierarchy; "
                  "setattr -unset keep_hierarchy; ")
        script += (unkeep + "flatten; ") if flatten else ""
        script += f"write_json {mem}; design -load premap; memory_map; "
        if flatten:
            script += unkeep + "flatten; "
        script += f"opt_clean; write_json {out}"
        try:
            subprocess.run(["yosys", "-q", "-p", script], check=True,
                           capture_output=True, text=True)
        except FileNotFoundError as e:
            raise DesignError("yosys is not on PATH") from e
        except subprocess.CalledProcessError as e:
            # Yosys's own message names the line it could not read, which is
            # what a reader needs; the Python traceback around it is not.
            last = (e.stderr or e.stdout or "").strip().splitlines()
            raise DesignError(last[-1] if last else
                              "yosys could not read the design") from e
        with open(out) as f:
            design = json.load(f)
        with open(mem) as f:
            design["dvh_memories"] = _memory_src(json.load(f))
        return design


def _memory_src(data: dict) -> dict:
    """Where each array was declared, keyed by module and by the name Yosys
    gives the memory.

    A memory keeps its name through `memory_map`: the registers it becomes
    are cells called `$memory\\mem[0]$25`, and flattening prefixes the
    instance path onto both the memory and those registers alike. Keying by
    the module as well as the name is what keeps two arrays called `mem` in
    two different modules apart.
    """
    found = {}
    for mname, m in data.get("modules", {}).items():
        for name, cell in m.get("cells", {}).items():
            if not cell["type"].startswith("$mem"):
                continue
            src = _relative(cell.get("attributes", {}).get("src", ""))
            if src:
                found.setdefault((mname, name), set()).add(src)
    return {f"{mod}\n{name}": next(iter(v))
            for (mod, name), v in found.items() if len(v) == 1}


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


def _fill_missing_src(mod: Module, memories: dict | None = None) -> None:
    """Give a cell a location when the netlist dropped its own.

    Lowering an array into registers synthesizes cells with no attributes at
    all, so sixteen registers arrived with nowhere to point. Three sources
    are tried, in decreasing order of how well they answer "where did this
    register come from", and none of them is an input net: an earlier
    version borrowed from inputs as well, and on a lowered array the input
    it found first was the clock, so every one of those sixteen registers
    pointed at the line the clock port was declared on.

    1. The array the register came from, recovered from the picture of the
       design taken before the memory passes ran.
    2. The net the cell drives, which is declared on the line the register
       is written on.
    3. The module's own declaration, which is coarse but true.
    """
    memories = memories or {}
    by_bit = {}
    for net in mod.netnames.values():
        src = _relative(net.get("attributes", {}).get("src", ""))
        if not src:
            continue
        for b in net["bits"]:
            if isinstance(b, int):
                by_bit.setdefault(b, src)
    for cell in mod.cells.values():
        if cell.src:
            continue
        cell.src = _from_memory(mod.name, cell.name, memories)
        if cell.src:
            continue
        for b in [b for p, bits in cell.conns.items()
                  if cell.dirs.get(p) == "output" for b in bits]:
            if isinstance(b, int) and b in by_bit:
                cell.src = by_bit[b]
                break
        if not cell.src:
            cell.src = mod.src


def _from_memory(mod: str, name: str, memories: dict) -> str:
    """The array a lowered register came from, if its cell name names one.

    `memory_map` names the registers it makes `$memory\\mem[0]$25`. Anything
    before that marker is the instance path flattening added, and the memory
    carries the same path, so the two are looked up together.
    """
    marker = "$memory\\"
    if marker not in name:
        return ""
    path, rest = name.split(marker, 1)
    # Flattening prefixes a public name with `u_store.` and a generated one
    # with `$flatten\u_store.`; the memory, whose name is public, gets the
    # first form, so the second has to be reduced to it before they match.
    path = path.removeprefix("$flatten\\")
    # The index and the counter come last; an array declared in a generate
    # block is `lane[0].mem[3]$25`, so the split is from the right.
    m = re.match(r"^(.*)\[\d+\]\$\d+$", rest)
    memid = path + (m.group(1) if m else rest.split("[")[0].split("$")[0])
    return memories.get(f"{mod}\n{memid}", "")


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
        mod = Module(mname, m.get("ports", {}), cells, m.get("netnames", {}),
                     _relative(m.get("attributes", {}).get("src", "")))
        mod.finish()
        _fill_missing_src(mod, data.get("dvh_memories", {}))
        # One naming for registers, shared by every walk: a bit-blasted
        # register must resolve to the same name registers() yields for it.
        mod.reg_of_bit = {b: name for name, cell in registers(mod)
                          for b in cell.conns.get("Q", [])
                          if isinstance(b, int)}
        mods[mname] = mod
    return mods


def load_flat(files, top) -> Module:
    """The flattened top module, for clock, reset and cone walks."""
    mods = _parse(_run_yosys(files, top, flatten=True))
    flat = mods[top]
    # Belt and braces, because this does not depend on knowing every
    # attribute Yosys honors: if anything is still instantiated, the walks
    # are about to analyze a fraction of the design and say nothing about
    # the rest. That is the one answer a gate must never get quietly.
    # A black box is the exception, and the only one: it has no contents to
    # analyze, which is what makes it a black box, and the walks already
    # treat its outputs as sources they cannot see behind.
    left = sorted({c.type for c in flat.cells.values()
                   if c.type in mods and mods[c.type].cells})
    if left:
        raise DesignError(
            f"{top} still instantiates {', '.join(left)} after flattening, "
            "so the registers inside them would not be analyzed at all")
    return flat


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
