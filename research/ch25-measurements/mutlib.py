"""mutlib.py -- shared pieces of the Chapter 25 mutation measurements.

The book's FIFO testbenches, read where they stand under examples/,
and a runner that builds one testbench against one design on
Verilator 5.052 with the book's flags and reports a verdict:

  killed     the testbench failed (non-zero exit or no PASS line)
  survived   the testbench passed
  timeout    the run did not finish in its limit (counted as killed,
             reported separately)
  stillborn  the mutant did not compile (excluded from every score)

Standard library only. Paths are relative to the repository root,
which every script changes to first.
"""
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EX = "examples"
FIXED = f"{EX}/ch09-temporal-properties/rtl/fifo_fixed.sv"
ORIG = f"{EX}/ch01-what-is-dv/rtl/fifo.sv"
CHK09 = f"{EX}/ch09-temporal-properties/fifo-checker"
TRACK = f"{EX}/ch19-formal-techniques/track-word/track.sv"

# The book's Verilator flags (examples/mk/sv.mk), plus --binary.
VFLAGS = ["--binary", "--timing", "--timescale", "1ns/1ps", "-Wall",
          "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "-Wno-PROCASSINIT"]

# name: (testbench sources, top, extra flags, runs, pass marker)
# Each run is a list of plusargs; the testbench passes only if every
# run exits 0 and prints the marker (None: exit status alone).
TBS = {
    "ch01-directed": (
        [f"{EX}/ch01-what-is-dv/sv-directed/tb_fifo_directed.sv"],
        "tb_fifo_directed", [], [[]], "PASS"),
    "ch01-random": (
        [f"{EX}/ch01-what-is-dv/sv-random/tb_fifo_random.sv"],
        "tb_fifo_random", [], [["+seed=1"]], "PASS"),
    "ch08-coverage": (
        [f"{EX}/ch08-functional-coverage/fifo-coverage/lint.vlt",
         f"{EX}/ch08-functional-coverage/fifo-coverage/tb_fifo_cov.sv"],
        "tb_fifo_cov", ["--coverage"],
        [["+bias=even", "+n=200", "+verilator+seed+1"],
         ["+bias=push", "+n=200", "+verilator+seed+1"]], None),
    "ch09-sva": (
        [f"{CHK09}/fifo_sva.sv", f"{CHK09}/fifo_bind.sv",
         f"{CHK09}/tb_fifo_sva.sv"],
        "tb_fifo_sva", ["-Wno-SYNCASYNCNET"],
        [["+verilator+seed+1"]], "PASS"),
}


def build(tb, design, mdir, extra=(), flags=None):
    """Build testbench TB against DESIGN (a list of files) in MDIR;
    FLAGS, when given, replace the testbench's own extra flags.
    Returns (ok, seconds, log tail)."""
    srcs, top, own, _, _ = TBS[tb]
    flags = own if flags is None else flags
    os.makedirs(mdir, exist_ok=True)
    cmd = (["verilator"] + VFLAGS + list(flags) + list(extra)
           + ["--top-module", top, "-Mdir", mdir] + list(design)
           + srcs)
    t = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode == 0, time.time() - t, p.stderr[-2000:]


def run(tb, mdir, plus=(), limit=20, runs=None):
    """Run a built testbench under each of its runs (RUNS, when given,
    replaces them). Returns (verdict, seconds, last output)."""
    _, top, _, own, marker = TBS[tb]
    runs = own if runs is None else runs
    exe = os.path.abspath(os.path.join(ROOT, mdir, "V" + top))
    t = time.time()
    out = ""
    for r in runs:
        try:
            p = subprocess.run([exe] + r + list(plus),
                               cwd=os.path.join(ROOT, mdir),
                               capture_output=True, text=True,
                               timeout=limit)
        except subprocess.TimeoutExpired:
            return "timeout", time.time() - t, ""
        out = p.stdout + p.stderr
        if p.returncode != 0 or (marker and marker not in p.stdout):
            return "killed", time.time() - t, out[-600:]
    return "survived", time.time() - t, out[-600:]


def pmap(fn, items, workers=4):
    """Map FN over ITEMS on WORKERS threads, keeping order."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
