"""run_sim.py -- the four FIFO testbenches of Chapters 1, 8 and 9
against every source mutant of mutate_src.py, and against the
repaired FIFO itself as the control (it must survive all four).

Each (mutant, testbench) pair is a separate Verilator build with the
book's flags plus -Wno-fatal, so that a mutant the book's lint would
reject still runs; the lint verdict is recorded separately (lint.tsv)
by a --lint-only pass with the book's flags as they are. Writes
sim.tsv: id, then one verdict per testbench, and prints a summary.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402

os.chdir(mutlib.ROOT)
BUILD = os.path.relpath(os.path.join(HERE, "build"), mutlib.ROOT)
SRC = os.path.join(BUILD, "src")


def ids():
    rows = [l.split("\t") for l in open(os.path.join(HERE, "mutants.tsv"))]
    return [r[0] for r in rows[1:]]


def design(mid):
    return [mutlib.FIXED] if mid == "orig" else [f"{SRC}/{mid}.sv"]


def job(arg):
    mid, tb = arg
    mdir = f"{BUILD}/obj/{mid}-{tb}"
    ok, bt, log = mutlib.build(tb, design(mid), mdir, ["-Wno-fatal"])
    if not ok:
        return mid, tb, "stillborn", bt, 0.0
    v, rt, _ = mutlib.run(tb, mdir)
    os.system(f"rm -rf {mdir}")
    return mid, tb, v, bt, rt


def lint(mid):
    import subprocess
    cmd = (["verilator", "--lint-only"] + mutlib.VFLAGS[1:]
           + ["--top-module", "fifo"] + design(mid))
    p = subprocess.run(cmd, capture_output=True, text=True)
    warn = sorted({w.split(":")[0].replace("%Warning-", "")
                   for w in p.stderr.split("\n")
                   if w.startswith("%Warning-")})
    return mid, ("clean" if p.returncode == 0 else
                 "rejected " + ",".join(warn) if warn else "error")


def main():
    t0 = time.time()
    os.system(f"python3 {HERE}/mutate_src.py {SRC} >/dev/null")
    mids = ["orig"] + ids()
    jobs = [(m, tb) for m in mids for tb in mutlib.TBS]
    res = mutlib.pmap(job, jobs)
    lints = dict(mutlib.pmap(lint, mids))
    table = {}
    btime = rtime = 0.0
    for mid, tb, v, bt, rt in res:
        table.setdefault(mid, {})[tb] = v
        btime += bt
        rtime += rt
    with open(os.path.join(HERE, "sim.tsv"), "w") as f:
        f.write("id\t" + "\t".join(mutlib.TBS) + "\tlint\n")
        for mid in mids:
            f.write(mid + "\t" + "\t".join(table[mid][tb]
                    for tb in mutlib.TBS) + "\t" + lints[mid] + "\n")
    print("control (repaired FIFO):",
          ", ".join(f"{tb} {table['orig'][tb]}" for tb in mutlib.TBS))
    live = [m for m in mids[1:]
            if "stillborn" not in table[m].values()]
    print(f"mutants: {len(mids) - 1}, compiled: {len(live)}")
    for tb in mutlib.TBS:
        k = sum(table[m][tb] in ("killed", "timeout") for m in live)
        print(f"  {tb:14s} killed {k:2d} of {len(live)}"
              f" ({100.0 * k / len(live):5.1f}%)")
    k = sum(any(table[m][tb] in ("killed", "timeout") for tb in mutlib.TBS)
            for m in live)
    print(f"  {'union':14s} killed {k:2d} of {len(live)}"
          f" ({100.0 * k / len(live):5.1f}%)")
    print(f"builds: {len(jobs)}, build time {btime:.0f} s,"
          f" run time {rtime:.1f} s (summed over 4 workers),"
          f" wall {time.time() - t0:.0f} s")
    os.system(f"rm -rf {BUILD}")


if __name__ == "__main__":
    main()
