"""mutlib.py -- the pieces every mutation example of the chapter shares.

The book's four FIFO testbenches, read where they stand under
examples/, and a runner that builds one testbench against one design
on Verilator with the book's flags and gives a verdict:

  killed     the testbench failed (non-zero exit or no PASS line)
  survived   the testbench passed
  timeout    the run did not finish in its limit (counted as a kill,
             reported apart)
  stillborn  the design did not compile (left out of every score)

Every tool runs from the repository root with paths relative to it,
so that nothing a run prints holds an absolute path, and so that the
source tags Yosys writes into a netlist name the file the same way on
every machine. Standard library only. Clopper-Pearson intervals and
the pinned-number checks come from the statistics chapter's library,
imported by path and not copied.
"""
import os
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
EX = "examples"
CH = f"{EX}/ch25-mutation-testing"
FIXED = f"{EX}/ch09-temporal-properties/rtl/fifo_fixed.sv"
ORIG = f"{EX}/ch01-what-is-dv/rtl/fifo.sv"
CHK09 = f"{EX}/ch09-temporal-properties/fifo-checker"
CH08 = f"{EX}/ch08-functional-coverage/fifo-coverage"
TRACK = f"{EX}/ch19-formal-techniques/track-word/track.sv"
CH19TCL = f"{EX}/ch19-formal-techniques/common/ch19.tcl"
INFORMAL_SH = f"{EX}/mk/informal.sh"

sys.path.insert(0, str(ROOT / EX / "ch21-statistics-random-testing"
                       / "common"))
import statlib  # noqa: E402

Checks = statlib.Checks

# The book's Verilator flags (examples/mk/sv.mk), plus --binary.
VFLAGS = ["--binary", "--timing", "--timescale", "1ns/1ps", "-Wall",
          "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "-Wno-PROCASSINIT"]

# Chapter 8's testbench writes a coverage database on every run; a
# mutation run has no use for it.
NOCOV = "+verilator+coverage+file+/dev/null"

# name: (testbench sources, top, extra flags, runs, pass marker)
# Each run is a list of plusargs; the testbench passes only if every
# run exits 0 and prints the marker (None: exit status alone).
# Chapter 8's testbench has no checker by design and runs its two
# mixes; Chapter 9's needs -Wno-SYNCASYNCNET, as its own runner sets.
TBS = {
    "ch01-directed": (
        [f"{EX}/ch01-what-is-dv/sv-directed/tb_fifo_directed.sv"],
        "tb_fifo_directed", [], [[]], "PASS"),
    "ch01-random": (
        [f"{EX}/ch25-mutation-testing/common/tb_fifo_random.sv"],
        "tb_fifo_random", [], [["+seed=1"]], "PASS"),
    "ch08-coverage": (
        [f"{CH08}/lint.vlt", f"{CH08}/tb_fifo_cov.sv"],
        "tb_fifo_cov", ["--coverage"],
        [["+bias=even", "+n=200", "+verilator+seed+1", NOCOV],
         ["+bias=push", "+n=200", "+verilator+seed+1", NOCOV]], None),
    "ch09-sva": (
        [f"{CHK09}/fifo_sva.sv", f"{CHK09}/fifo_bind.sv",
         f"{CHK09}/tb_fifo_sva.sv"],
        "tb_fifo_sva", ["-Wno-SYNCASYNCNET"],
        [["+verilator+seed+1"]], "PASS"),
}
NAMES = list(TBS)
DEAD = ("killed", "timeout")


def rel(path):
    """PATH relative to the repository root, for a command line."""
    return os.path.relpath(os.path.abspath(path), ROOT)


def build(tb, design, mdir, extra=(), flags=None, tbs=None):
    """Build testbench TB against DESIGN (a list of files) in MDIR;
    FLAGS, when given, replace the testbench's own extra flags; TBS
    replaces the testbench table. Returns (ok, seconds, stderr)."""
    srcs, top, own, _, _ = (tbs or TBS)[tb]
    flags = own if flags is None else flags
    os.makedirs(mdir, exist_ok=True)
    cmd = (["verilator"] + VFLAGS + list(flags) + list(extra)
           + ["--top-module", top, "-Mdir", rel(mdir)]
           + [rel(ROOT / d) for d in design] + list(srcs))
    t = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode == 0, time.time() - t, p.stderr


def run(tb, mdir, plus=(), limit=20, runs=None, tbs=None):
    """Run a built testbench under each of its runs (RUNS, when given,
    replaces them), PLUS appended to each. Returns (verdict, seconds,
    output of the last run)."""
    _, top, _, own, marker = (tbs or TBS)[tb]
    runs = own if runs is None else runs
    exe = os.path.abspath(os.path.join(mdir, "V" + top))
    t = time.time()
    out = ""
    for r in runs:
        try:
            p = subprocess.run([exe] + list(r) + list(plus), cwd=mdir,
                               capture_output=True, text=True,
                               timeout=limit)
        except subprocess.TimeoutExpired:
            return "timeout", time.time() - t, ""
        out = p.stdout + p.stderr
        if p.returncode != 0 or (marker and marker not in p.stdout):
            return "killed", time.time() - t, out
    return "survived", time.time() - t, out


def pmap(fn, items, workers=4):
    """Map FN over ITEMS on WORKERS threads, keeping order."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def version(program):
    """The version line a tool prints, trimmed to what does not vary."""
    if program == "verilator":
        out = subprocess.run(["verilator", "--version"],
                             capture_output=True, text=True).stdout
        return " ".join(out.split()[:2])
    if program == "yosys":
        out = subprocess.run(["yosys", "-V"], capture_output=True,
                             text=True).stdout.split()
        return f"{out[0]} {out[1]} (git {out[4].rstrip(',')})"
    if program == "informal":
        out = subprocess.run(["informal", "--version"],
                             capture_output=True, text=True).stdout
        return out.strip() + " (pinned at 5114330)"
    return "?"


def cp(k, n):
    """The two-sided 95% Clopper-Pearson interval of the statistics
    chapter, for k successes in n."""
    return statlib.cp_interval(k, n, 0.95)


def fmt_cp(k, n):
    lo, hi = cp(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]"


def table_md(path, header, rows, caption, widths=None):
    """Write a generated Markdown table through the formal chapter's
    tables.py, imported by path."""
    sys.path.insert(0, str(ROOT / EX / "ch18-formal-property-verification"
                           / "common"))
    import tables  # noqa: E402
    rows = [[tables.cell(c) for c in r] for r in rows]
    grid = bool(widths) or any("|" in c for r in rows + [header]
                               for c in r)
    tables.write(path, header, rows, caption, grid=grid, widths=widths)


def wrap(text, indent="  ", width=76):
    """TEXT folded at spaces to WIDTH columns, each continuation line
    indented by INDENT, so that no printed line passes 80 columns."""
    import textwrap
    return textwrap.fill(text, width, subsequent_indent=indent,
                         break_on_hyphens=False, break_long_words=False)


def need(*programs):
    """Print the one line the checker reads as a skip, and stop, when
    a program this example needs is not installed."""
    import shutil
    for p in programs:
        if not shutil.which(p):
            print(f"skipped: {p} is not on the PATH")
            sys.exit(0)


def pin_measured(C, path, want):
    """Pin a committed measured file (measure.out, pop.tsv) by its
    SHA-256, so that an edit to any line, spliced or not, fails the
    default run. Under MEASURE=1 the file has just been rewritten:
    print its new digest, to be pinned in the script, instead."""
    import hashlib
    got = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    name = rel(path)
    if os.environ.get("MEASURE") == "1":
        print(f"{name} rewritten: pin sha256 {got}")
    else:
        C.pin(f"{name} sha256", got, want)
