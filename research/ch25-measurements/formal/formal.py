"""formal.py -- InFormal runs for the Chapter 25 measurements: the
book's FIFO property set against a mutant (does it kill it?), and a
miter of the repaired FIFO against a mutant (is it equivalent?).

A design is ("src", path) for a source mutant (module fifo) or
("net", path) for a Yosys netlist mutant (module fifo_m, wrapped by
fifo_fwrap.sv). Every run goes through the book's runner
examples/mk/informal.sh with one engine selected for each prove,
as the book's formal examples do.

The property set is Chapter 19's (`mutants/`): Chapter 9's FIFO
checker bound as it ships, Chapter 18's EmptyPtrs_A and Chapter 19's
tracked-word check a_integrity.
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402

R = mutlib.ROOT
COMMON = f"{R}/examples/ch19-formal-techniques/common/ch19.tcl"
SVA = [f"{R}/{mutlib.CHK09}/fifo_sva.sv",
       f"{R}/{mutlib.CHK09}/fifo_bind.sv"]


def files(design, work):
    """The files that make module fifo (kill) or fifo_m (miter)."""
    kind, path = design
    if kind == "src":
        renamed = os.path.join(work, "fifo_m.sv")
        with open(path) as f, open(renamed, "w") as g:
            g.write(re.sub(r"^module fifo ", "module fifo_m ", f.read(),
                           flags=re.M))
        return [path], [renamed]
    return [path, f"{HERE}/fifo_fwrap.sv"], [path]


def shell(tcl, work, limit):
    """Run one script; return (report text, seconds)."""
    os.makedirs(work, exist_ok=True)
    script = os.path.join(work, "run.tcl")
    with open(script, "w") as f:
        f.write(tcl)
    t = time.time()
    try:
        p = subprocess.run(["bash", f"{R}/examples/mk/informal.sh",
                            script, os.path.join(work, "w")],
                           capture_output=True, text=True, timeout=limit)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
    return out, time.time() - t


ROWS = """
foreach p [get_property_list -include {type assert}] {
  puts "ROW [lindex [split $p .] end] [get_status $p] [depth $p]"
}
finish
"""


def rows(out):
    return {m.group(1): (m.group(2), int(m.group(3)))
            for m in re.finditer(r"^ROW (\S+) (\S+) (-?\d+)$", out, re.M)}


def kill(design, work, bmc="5s"):
    """The property set against DESIGN by BMC. Returns
    ({property: (status, depth)}, seconds)."""
    os.makedirs(work, exist_ok=True)
    fifo, _ = files(design, work)
    srcs = " ".join(fifo + SVA + [f"{R}/{mutlib.TRACK}"])
    tcl = f"""source {COMMON}
design [list {srcs}] track
catch {{cover -disable *_C}}
assume -name m_sd {{$stable(sd)}}
assert -name a_integrity {{in_q && ahead == '0 |-> rd_data == sd}}
assert -name EmptyPtrs_A {{empty |-> u.wr_ptr == u.rd_ptr}}
one informal-bmc {bmc} -all
""" + ROWS
    out, t = shell(tcl, work, 300)
    return rows(out), t, out


EQ = "full_a == full_b && empty_a == empty_b && (empty_a || rd_a == rd_b)"


def equiv(design, work, bmc="10s", proof="30s", ric3="120s"):
    """Miter of the repaired FIFO and DESIGN. Returns (verdict,
    detail, seconds): 'differs' with the depth of the distinguishing
    trace, 'equivalent' with the engine that proved it, or 'unknown'."""
    os.makedirs(work, exist_ok=True)
    _, m = files(design, work)
    srcs = " ".join([f"{R}/{mutlib.FIXED}"] + m + [f"{HERE}/miter.sv"])
    t0 = time.time()
    for engine, limit in (("informal-bmc", bmc), ("informal-ic3", proof),
                          ("ric3-ic3", ric3)):
        tcl = f"""source {COMMON}
design [list {srcs}] miter
assert -name Eq_A {{{EQ}}}
one {engine} {limit} -all
""" + ROWS
        out, _ = shell(tcl, os.path.join(work, engine), 300)
        st, d = rows(out).get("Eq_A", ("error", -1))
        if st == "cex":
            return "differs", f"depth {d} ({engine})", time.time() - t0
        if st == "proven":
            return "equivalent", engine, time.time() - t0
        if st == "error":
            return "error", out[-300:], time.time() - t0
    return "unknown", "no verdict", time.time() - t0
