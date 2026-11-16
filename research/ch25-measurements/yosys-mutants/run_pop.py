"""run_pop.py -- the four FIFO testbenches against every mutation
Yosys's `mutate` pass lists for the repaired FIFO (the population),
each testbench built once against the netlist with all mutations
behind a select and run once per mutation with +mut=N.

Also runs Chapter 1's random testbench under seeds 1-8 for every
mutation and records the first seed that kills it, for the
kill-rate-against-seeds curve. Writes pop.tsv (id, mode, source line,
cell kind, one verdict per testbench, first killing seed of
ch01-random or 0) and prints a summary.

  run_pop.py NETDIR    NETDIR from gen.sh
"""
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import mutlib  # noqa: E402

os.chdir(mutlib.ROOT)
NET = os.path.abspath(sys.argv[1])
BUILD = os.path.join(NET, "obj")
SEEDS = range(1, 9)
DESIGN = [os.path.join(NET, "fifo_mut.v"), os.path.join(HERE, "fifo_wrap.sv")]
# --no-assert-case: Yosys writes each $pmux as a casez marked
# "synopsys parallel_case", and Verilator turns that pragma into an
# assertion. A mutation on a select bit then fails that assertion in
# any testbench, even one with no checker (383 mutations "killed" by
# Chapter 8's testbench in the first run, run_pop_assert_case.log).
# Concurrent assertions, Chapter 9's checker among them, stay on.
QUIET = ["-Wno-fatal", "-Wno-lint", "-Wno-style", "--no-assert-case"]
# Chapter 8's testbench is built with --coverage-user, not --coverage:
# its covergroups report the same percentages (75.86 for run A), and
# the line and toggle points of the 48,000-line netlist made each run
# 1.2 s instead of 0.01 s. Its database goes to /dev/null.
FLAGS = {"ch08-coverage": ["--coverage-user"]}
PLUS = {"ch08-coverage": ["+verilator+coverage+file+/dev/null"]}


def parse(line):
    """(mode, source line, cell kind) of one `mutate` command."""
    mode = re.search(r"-mode (\w+)", line).group(1)
    src = re.search(r"-src \S*?:(\d+)\.", line)
    cell = re.search(r"-cell \$(\w+)\$", line)
    return mode, src.group(1) if src else "-", \
        cell.group(1) if cell else "-"


def main():
    t0 = time.time()
    lines = [l for l in open(os.path.join(NET, "list.txt"))]
    n = len(lines) - 1                 # line 0 is the 'none' mutation
    for tb in mutlib.TBS:
        ok, bt, log = mutlib.build(tb, DESIGN, f"{BUILD}/{tb}", QUIET,
                                   FLAGS.get(tb))
        print(f"build {tb}: {'ok' if ok else 'FAILED'} {bt:.1f} s")
        if not ok:
            print(log)
            sys.exit(1)
    tbuild = time.time() - t0

    def one(k):
        row = [mutlib.run(tb, f"{BUILD}/{tb}",
                          [f"+mut={k}"] + PLUS.get(tb, []))[0]
               for tb in mutlib.TBS]
        first = 0
        for s in SEEDS:
            v = mutlib.run("ch01-random", f"{BUILD}/ch01-random",
                           [f"+mut={k}"], runs=[[f"+seed={s}"]])[0]
            if v != "survived":
                first = s
                break
        return row, first

    t1 = time.time()
    res = mutlib.pmap(one, range(n + 1))
    trun = time.time() - t1
    ctrl, _ = res[0]
    print("control (mutation 0):", ", ".join(
        f"{tb} {v}" for tb, v in zip(mutlib.TBS, ctrl)))
    with open(os.path.join(HERE, "pop.tsv"), "w") as f:
        f.write("id\tmode\tline\tcell\t" + "\t".join(mutlib.TBS)
                + "\tfirst_seed\n")
        for k in range(1, n + 1):
            mode, ln, cell = parse(lines[k])
            row, first = res[k]
            f.write(f"{k}\t{mode}\t{ln}\t{cell}\t" + "\t".join(row)
                    + f"\t{first}\n")
    print(f"mutations: {n}")
    dead = lambda v: v in ("killed", "timeout")  # noqa: E731
    for i, tb in enumerate(mutlib.TBS):
        k = sum(dead(res[j][0][i]) for j in range(1, n + 1))
        print(f"  {tb:14s} killed {k:5d} of {n} ({100.0 * k / n:5.1f}%)")
    k = sum(any(dead(v) for v in res[j][0]) for j in range(1, n + 1))
    print(f"  {'union':14s} killed {k:5d} of {n} ({100.0 * k / n:5.1f}%)")
    acc = 0
    for s in SEEDS:
        acc += sum(res[j][1] == s for j in range(1, n + 1))
        print(f"  ch01-random, seeds 1..{s}: killed {acc} "
              f"({100.0 * acc / n:5.1f}%)")
    print(f"time: builds {tbuild:.0f} s, runs {trun:.0f} s wall "
          f"({(n + 1) * (len(mutlib.TBS) + 1)}+ executions, 4 workers)")


if __name__ == "__main__":
    main()
