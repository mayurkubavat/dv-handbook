"""miter.py -- the chapter's two formal judges of a mutant, on InFormal.

A miter: the repaired FIFO (module fifo) and a mutant (module fifo_m)
side by side on the same inputs (common/miter.sv), with one assertion
that their ports agree, EQ below. What EQ compares is the definition
of "equivalent" these examples use: full and empty always, rd_data
whenever the original is not empty, because the memory is not reset
and the contract gives an empty FIFO's rd_data no meaning. A
counterexample is a trace on which the two differ; a proof (rIC3's
IC3 here) is the equivalence. Bounded search can only ever refute.

The property set: the formal-techniques chapter's, read by path
(that chapter's `mutants/` example): the temporal-properties
chapter's checker bound as it ships, the pointer property
EmptyPtrs_A, and the tracked-word check a_integrity on track.sv. A
counterexample to any of them kills the mutant.

Every script goes through the book's runner examples/mk/informal.sh
and sources the formal-techniques chapter's ch19.tcl (`design`,
`one`, `depth`, `expect`), which loads the formal chapter's
proof.tcl. Paths in the scripts are absolute; the reports name
properties only.
"""
import re
import subprocess

from mutlib import CH19TCL, CHK09, FIXED, HERE, INFORMAL_SH, ROOT, TRACK

EQ = ("full_a == full_b && empty_a == empty_b"
      " && (empty_a || rd_a == rd_b)")
MITER = HERE / "miter.sv"
FWRAP = HERE / "fifo_fwrap.sv"
SVA = [ROOT / CHK09 / "fifo_sva.sv", ROOT / CHK09 / "fifo_bind.sv"]
# The property set in the fixed order a stop-at-first-kill run tries
# it: the checker's flag and counter properties, then the data and
# pointer properties, then the rest.
PROPS = ["EmptyExact_A", "Sync_A", "a_integrity", "EmptyPtrs_A",
         "FullBackward_A", "NoOverflow_A", "FullForward_A",
         "PushFull_A", "PopEmpty_A"]
ROWS = """
foreach p [get_property_list -include {type assert}] {
  puts "ROW [lindex [split $p .] end] [get_status $p] [depth $p]"
}
"""


def head():
    return f"source {ROOT / CH19TCL}\n"


def shell(tcl, work, timeout=600):
    """Run one script through the book's runner; (status, report)."""
    work.mkdir(parents=True, exist_ok=True)
    script = work / "run.tcl"
    script.write_text(tcl)
    p = subprocess.run(["bash", str(ROOT / INFORMAL_SH), str(script),
                        str(work / "w")], capture_output=True, text=True,
                       timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def rows(out):
    """{property: (status, depth)} from the ROW lines of a report."""
    return {m.group(1): (m.group(2), int(m.group(3)))
            for m in re.finditer(r"^ROW (\S+) (\S+) (-?\d+)$", out, re.M)}


def rename(src_text, work, name="fifo_m"):
    """Write a mutant's text with its module renamed for the miter."""
    work.mkdir(parents=True, exist_ok=True)
    out = work / f"{name}.sv"
    out.write_text(re.sub(r"^module fifo ", f"module {name} ", src_text,
                          flags=re.M))
    return out


def miter_tcl(mutant, engine, limit, eq=EQ, files=None):
    """A script: the miter of the repaired FIFO and MUTANT (a file
    holding module fifo_m), Eq_A proved with one engine."""
    srcs = files or [ROOT / FIXED, mutant, MITER]
    return (head() + f"design [list {' '.join(map(str, srcs))}] miter\n"
            f"assert -name Eq_A {{{eq}}}\n"
            f"one {engine} {limit} -all\n" + ROWS + "finish\n")


def miter(mutant, work, engine, limit, eq=EQ):
    """(status, depth) of Eq_A, and the report."""
    rc, out = shell(miter_tcl(mutant, engine, limit, eq), work)
    return rows(out).get("Eq_A", ("error", -1)), out


def setup_tcl(fifo_files):
    """The property set on a design whose module fifo is FIFO_FILES:
    the checker bound, the tracked word, the pointer property."""
    srcs = " ".join(map(str, list(fifo_files) + SVA + [ROOT / TRACK]))
    return (f"design [list {srcs}] track\n"
            "catch {cover -disable *_C}\n"
            "assume -name m_sd {$stable(sd)}\n"
            "assert -name a_integrity "
            "{in_q && ahead == '0 |-> rd_data == sd}\n"
            "assert -name EmptyPtrs_A {empty |-> u.wr_ptr == u.rd_ptr}\n")


def kill_first_tcl(fifo_files, limit, props=PROPS):
    """A script: the properties one at a time in PROPS order, each by
    BMC for LIMIT, stopping at the first counterexample. Prints
    FIRST <property> <depth>, FIRST - -1 when none failed, or FIRST
    refused -1 when the front end refused the design."""
    plist = " ".join(props)
    return (head() + setup_tcl(fifo_files) + f"""
set first "- -1"
if {{[catch {{full {props[0]}}}]}} {{
  # The checker's properties are missing when the front end refused
  # the design; one prove prints the tool's reason in its report.
  one informal-bmc 1s -all
  set props {{}}
  set first "refused -1"
}} else {{
  set props {{{plist}}}
}}
foreach p $props {{
  one informal-bmc {limit} -property [full $p]
  if {{[get_status [full $p]] eq "cex"}} {{
    set first "$p [depth $p]"
    break
  }}
}}
puts "FIRST $first"
""" + "finish\n")


def kill_all_tcl(fifo_files, limit):
    """A script: every property by BMC for LIMIT each (the full
    per-property matrix)."""
    return (head() + setup_tcl(fifo_files)
            + f"one informal-bmc {limit} -all\n" + ROWS + "finish\n")


def first(out):
    m = re.search(r"^FIRST (\S+) (-?\d+)$", out, re.M)
    return (m.group(1), int(m.group(2))) if m else ("error", -1)


def refusal(out):
    """The front end's message when it refuses a design, else None."""
    m = re.search(r"svlang: \S*?:(\d+):\d+: ([^\n]*)", out) or \
        re.search(r"svlang: \S*?(\d+): ([^\n]*)", out)
    return f"line {m.group(1)}: {m.group(2)}" if m else None


def bmc_then_ric3(mutant, work, bmc="3s", ric3="120s"):
    """The miter of MUTANT by bounded search, then by rIC3's IC3.
    Returns [(engine, status, depth)] for the runs made: rIC3 runs
    only when the bounded search found no difference."""
    out = []
    (st, d), _ = miter(mutant, work / "bmc", "informal-bmc", bmc)
    out.append(("informal-bmc", st, d))
    if st != "cex":
        (st, d), _ = miter(mutant, work / "ric3", "ric3-ic3", ric3)
        out.append(("ric3-ic3", st, d))
    return out


def say(engine, status, depth, limit):
    """One line for a miter verdict, as the examples print it."""
    if status == "cex":
        return f"{engine}: differs at depth {depth}"
    if status == "proven":
        return f"{engine}: proved equivalent"
    return f"{engine}: no verdict in {limit}"


def show_eq(eq=EQ, lead="miter compares: "):
    """The comparison as two printed lines at most."""
    if " && (" in eq and len(lead + eq) > 72:
        a, b = eq.split(" && (", 1)
        return f"{lead}{a}\n{' ' * len(lead)}&& ({b}"
    return lead + eq
