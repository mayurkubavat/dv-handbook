"""rand_init.py -- the source mutants no testbench killed, run again
with every register starting from a random value instead of zero.

Verilator gives every variable without an initial value the value 0
by default. Built with --x-initial unique and run with
+verilator+rand+reset+2, such variables start from values drawn from
the run's seed (+verilator+seed+S, S = 1..5 here). The repaired FIFO
is the control: it must pass every run, since its contract never
reads an entry it has not written.

Writes rand_init.tsv: id, testbench, the seeds that killed it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402

os.chdir(mutlib.ROOT)
BUILD = os.path.relpath(os.path.join(HERE, "build-ri"), mutlib.ROOT)
SRC = os.path.join(BUILD, "src")
IDS = ["orig", "m05", "m09", "m11", "m13", "m32", "m36", "m43", "m44"]
SEEDS = range(1, 6)


def job(arg):
    mid, tb = arg
    design = [mutlib.FIXED] if mid == "orig" else [f"{SRC}/{mid}.sv"]
    mdir = f"{BUILD}/obj/{mid}-{tb}"
    ok, _, log = mutlib.build(tb, design, mdir,
                              ["-Wno-fatal", "--x-initial", "unique"])
    if not ok:
        return mid, tb, "stillborn"
    kills = [str(s) for s in SEEDS
             if mutlib.run(tb, mdir, ["+verilator+rand+reset+2",
                                      f"+verilator+seed+{s}"])[0]
             != "survived"]
    return mid, tb, ",".join(kills) or "-"


def main():
    os.system(f"python3 {HERE}/mutate_src.py {SRC} >/dev/null")
    res = mutlib.pmap(job, [(m, tb) for m in IDS for tb in mutlib.TBS])
    with open(os.path.join(HERE, "rand_init.tsv"), "w") as f:
        f.write("id\t" + "\t".join(mutlib.TBS) + "\n")
        for m in IDS:
            f.write(m + "\t" + "\t".join(v for mid, tb, v in res
                                         if mid == m) + "\n")
    print(open(os.path.join(HERE, "rand_init.tsv")).read(), end="")
    os.system(f"rm -rf {BUILD}")


if __name__ == "__main__":
    main()
