"""pop.py -- the whole netlist population, whose kill rates are known
exactly, and what sampling from it gives.

    python3 pop.py              Python over the committed pop.tsv
                                (about 30 seconds)
    MEASURE=1 python3 pop.py    first regenerate pop.tsv: every one of
                                the 9,281 mutations behind one select,
                                the four testbenches built once each,
                                9,282 runs of each, and the random
                                test's seeds 1-8 for the seed curve
                                (a few minutes); summary to measure.out

pop.tsv holds, for every mutation: its number in Yosys's list, mode,
source line, cell type, one verdict for each testbench, and the first
of seeds 1-8 at which Chapter 1's random test kills it (0 for none).
From it:
  1. population kill rates and the random test's seed curve;
  2. one uniform sample (seed 1) at n = 30, 100, 300, 1000, nested,
     with the 95% Clopper-Pearson interval of the statistics chapter;
  3. 2,000 samples at each n: how often the interval holds the
     population rate, and its mean width, beside the worst-case
     half-widths by Chebyshev and by the normal approximation;
  4. the population kill rate by mutation mode.
"""
import datetime
import math
import os
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import mutlib  # noqa: E402
import yosysmut  # noqa: E402

B = HERE / "build"
POP = HERE / "pop.tsv"
SEEDS = range(1, 9)
NS = (30, 100, 300, 1000)
_CP = {}


def cp(k, n):
    if (k, n) not in _CP:
        _CP[(k, n)] = mutlib.cp(k, n)
    return _CP[(k, n)]


def regenerate():
    t0 = time.time()
    B.mkdir(parents=True, exist_ok=True)
    cmds, _ = yosysmut.population(B)
    N = len(cmds) - 1
    net = yosysmut.select_netlist(cmds[1:], B / "fifo_mut.v")
    nlines = len(net.read_text().splitlines())
    dirs = yosysmut.build_netlist(B / "obj", net, mutlib.NAMES)
    tb_build = time.time() - t0

    def one(k):
        row = [mutlib.run(tb, dirs[tb], [f"+mut={k}"])[0]
               for tb in mutlib.NAMES]
        first = 0
        for s in SEEDS:
            v = mutlib.run("ch01-random", dirs["ch01-random"],
                           [f"+mut={k}"], runs=[[f"+seed={s}"]])[0]
            if v != "survived":
                first = s
                break
        return row, first

    t1 = time.time()
    res = mutlib.pmap(one, range(N + 1))
    ctrl = res[0][0]
    with POP.open("w") as f:
        f.write("id\tmode\tline\tcell\t" + "\t".join(mutlib.NAMES)
                + "\tfirst_seed\n")
        for k in range(1, N + 1):
            mode, ln, cell = yosysmut.parse(cmds[k])
            row, first = res[k]
            f.write(f"{k}\t{mode}\t{ln}\t{cell}\t" + "\t".join(row)
                    + f"\t{first}\n")
    lines = [f"measure.out -- written by MEASURE=1 make run on "
             f"{datetime.date.today().isoformat()}",
             f"tools: {mutlib.version('yosys')}; "
             f"{mutlib.version('verilator')}",
             f"netlist: {N} mutations behind mutsel, {nlines} lines",
             f"list, netlist and 4 builds: {tb_build:.0f} s",
             f"runs: {(N + 1) * 4} plus the seed sweep, "
             f"{time.time() - t1:.0f} s wall on 4 workers",
             "control (mutation 0): " + ", ".join(
                 v for v in ctrl)]
    (HERE / "measure.out").write_text("\n".join(lines) + "\n")
    return lines


def load():
    rows = [x.rstrip("\n").split("\t") for x in POP.open()]
    head, rows = rows[0], rows[1:]
    tbs = head[4:-1]
    kill = {tb: [r[4 + i] in mutlib.DEAD for r in rows]
            for i, tb in enumerate(tbs)}
    kill["union"] = [any(kill[tb][j] for tb in tbs)
                     for j in range(len(rows))]
    return rows, tbs, kill


def main():
    C = mutlib.Checks()
    measured = []
    if os.environ.get("MEASURE") == "1":
        mutlib.need("yosys")
        measured = regenerate()
    rows, tbs, kill = load()
    N = len(rows)
    names = tbs + ["union"]
    print(f"population: {N} netlist mutations of fifo_fixed.sv (Yosys 0.68,"
          " after prep),")
    print("  from the committed pop.tsv")
    sec1 = ["1. population kill rates"]
    k = {tb: sum(kill[tb]) for tb in names}
    p = {tb: k[tb] / N for tb in names}
    for tb in names:
        sec1.append(f"  {tb:14s} {k[tb]:5d}/{N} = {p[tb]:.4f}")
    C.pin("population kills", [k[tb] for tb in names],
          [2725, 8265, 0, 351, 8300])
    acc = 0
    curve = []
    for s in SEEDS:
        acc += sum(r[-1] == str(s) for r in rows)
        curve.append(acc)
        sec1.append(f"  ch01-random, seeds 1..{s}: killed {acc} "
                    f"({100.0 * acc / N:.1f}%)")
    print("\n".join(sec1))
    if measured:
        with (HERE / "measure.out").open("a") as f:
            f.write("\n".join(sec1) + "\n")
    C.pin("seed curve", curve, [8265, 8343, 8355, 8355, 8355, 8355,
                                8355, 8355])

    print("2. one uniform sample (seed 1), nested, 95% Clopper-Pearson")
    draw = [j - 1 for j in yosysmut.uniform(N, max(NS), 1)]
    for n in NS:
        idx = draw[:n]
        print(f"  n = {n}")
        for tb in names:
            kk = sum(kill[tb][j] for j in idx)
            lo, hi = cp(kk, n)
            print(f"    {tb:14s} {kk:4d}/{n} [{lo:.3f}, {hi:.3f}]"
                  f"{'' if lo <= p[tb] <= hi else '  misses'}")
            if n == 100 and tb == "ch01-directed":
                C.pin("directed at n = 100", (kk, round(lo, 3),
                                              round(hi, 3)),
                      (30, 0.212, 0.4))
    print("3. 2,000 samples at each n: how often the 95% interval holds")
    print("   the population rate, and its mean width")
    R = 2000
    cov = {}
    for n in NS:
        rng = random.Random(n)
        hit = {tb: 0 for tb in names}
        width = {tb: 0.0 for tb in names}
        for _ in range(R):
            idx = rng.sample(range(N), n)
            for tb in names:
                kk = sum(kill[tb][j] for j in idx)
                lo, hi = cp(kk, n)
                hit[tb] += lo <= p[tb] <= hi
                width[tb] += hi - lo
        cheb = 1 / math.sqrt(4 * n * 0.05)
        norm = 1.96 * math.sqrt(0.25 / n)
        print(f"  n = {n}: worst-case half-width Chebyshev {cheb:.3f},"
              f" normal {norm:.3f}")
        for tb in names:
            cov[(n, tb)] = hit[tb] / R
            print(f"    {tb:14s} coverage {hit[tb] / R:.3f}  mean width "
                  f"{width[tb] / R:.3f}")
    worst = min(cov.values())
    print(f"  lowest coverage over every n and testbench: {worst:.3f}")
    C.holds("every coverage at least 0.94", worst >= 0.94)
    print("4. population kill rate by mode")
    print(f"  {'mode':7s} {'n':>5s}" + "".join(f"{tb.split('-')[-1]:>10s}"
                                             for tb in names))
    for m in sorted({r[1] for r in rows}):
        j = [i for i, r in enumerate(rows) if r[1] == m]
        print(f"  {m:7s} {len(j):5d}" + "".join(
            f"{sum(kill[tb][i] for i in j) / len(j):10.3f}"
            for tb in names))
    if measured:
        print("\n".join(measured))
    C.pin("measure.out agrees with pop.tsv", (HERE / "measure.out")
          .read_text().splitlines()[6:], sec1)
    C.report()
    print("verdict: the population rates are known, and the sampled "
          "intervals cover them")


if __name__ == "__main__":
    main()
