"""sample.py -- a sampled mutation score with a confidence interval,
checked against the population it was drawn from.

Reads ../yosys-mutants/pop.tsv, where every one of the 9,281 netlist
mutations was run against each testbench, so the population kill rate
of each testbench is known exactly. Then, for sample sizes n = 30,
100, 300 and 1000:
  s.1 one uniform sample (seed 1): k killed of n and the 95%
      Clopper-Pearson interval of the statistics chapter;
  s.2 2000 samples: how often the interval contains the population
      rate (its coverage), and its mean width; beside it the
      Chebyshev and normal half-widths Gopinath et al. use.
  s.3 the kill rate by mutation mode, population.
  s.4 if ../formal/ysample.tsv exists, the equivalent fraction from
      the formal sample with its interval, and the kill rate of each
      testbench among that sample's non-equivalent mutants.
Standard library only; Clopper-Pearson from the Chapter 21 library.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ch21-measurements"))
import statlib  # noqa: E402

POP = os.path.join(HERE, "..", "yosys-mutants", "pop.tsv")
YS = os.path.join(HERE, "..", "formal", "ysample.tsv")
DEAD = ("killed", "timeout")
_CP = {}


def cp(k, n):
    """95% Clopper-Pearson interval, memoized: k repeats across
    samples, and each interval is two bisections."""
    if (k, n) not in _CP:
        _CP[(k, n)] = statlib.cp_interval(k, n, 0.95)
    return _CP[(k, n)]


def load():
    rows = [l.rstrip("\n").split("\t") for l in open(POP)]
    head, rows = rows[0], rows[1:]
    tbs = head[4:-1]
    kill = {tb: [r[4 + i] in DEAD for r in rows] for i, tb in enumerate(tbs)}
    kill["union"] = [any(kill[tb][j] for tb in tbs) for j in range(len(rows))]
    return head, rows, tbs, kill


def main():
    head, rows, tbs, kill = load()
    N = len(rows)
    names = tbs + ["union"]
    print(f"population: {N} mutations")
    p = {tb: sum(kill[tb]) / N for tb in names}
    for tb in names:
        print(f"  {tb:14s} population kill rate {sum(kill[tb]):5d}/{N}"
              f" = {p[tb]:.4f}")
    print("s.1 one uniform sample per n (seed 1), 95% Clopper-Pearson")
    for n in (30, 100, 300, 1000):
        idx = random.Random(1).sample(range(N), n)
        cells = []
        for tb in names:
            k = sum(kill[tb][j] for j in idx)
            lo, hi = cp(k, n)
            cells.append(f"{tb} {k}/{n} [{lo:.3f},{hi:.3f}]")
        print(f"  n={n:4d}: " + "; ".join(cells))
    print("s.2 2000 samples per n: coverage of the 95% CP interval,"
          " mean width")
    R = 2000
    for n in (30, 100, 300, 1000):
        rng = random.Random(n)
        hit = {tb: 0 for tb in names}
        width = {tb: 0.0 for tb in names}
        for _ in range(R):
            idx = rng.sample(range(N), n)
            for tb in names:
                k = sum(kill[tb][j] for j in idx)
                lo, hi = cp(k, n)
                hit[tb] += lo <= p[tb] <= hi
                width[tb] += hi - lo
        cheb = 1 / math.sqrt(4 * n * 0.05)
        norm = 1.96 * math.sqrt(0.25 / n)
        print(f"  n={n:4d}: " + "; ".join(
            f"{tb} {hit[tb] / R:.3f} w={width[tb] / R:.3f}"
            for tb in names)
            + f"; worst-case half-width Chebyshev {cheb:.3f},"
              f" normal {norm:.3f}")
    print("s.3 population kill rate by mutation mode")
    modes = sorted({r[1] for r in rows})
    for m in modes:
        j = [i for i, r in enumerate(rows) if r[1] == m]
        print(f"  {m:7s} {len(j):5d}: " + "  ".join(
            f"{tb} {sum(kill[tb][i] for i in j) / len(j):.3f}"
            for tb in names))
    if not os.path.exists(YS):
        return
    print("s.4 formal sample (../formal/ysample.tsv)")
    ys = [l.rstrip("\n").split("\t") for l in open(YS)][1:]
    n = len(ys)
    eq = [r for r in ys if r[2] == "equivalent"]
    unk = [r for r in ys if r[2] not in ("equivalent", "differs")]
    lo, hi = statlib.cp_interval(len(eq), n, 0.95)
    print(f"  {n} sampled; equivalent {len(eq)}, undecided {len(unk)};"
          f" equivalent fraction {len(eq) / n:.3f} [{lo:.3f},{hi:.3f}]")
    ne = [int(r[0]) - 1 for r in ys if r[2] == "differs"]
    fk = sum(r[1] != "-" for r in ys if r[2] == "differs")
    m = len(ne)
    for tb in names:
        k = sum(kill[tb][j] for j in ne)
        lo, hi = statlib.cp_interval(k, m, 0.95)
        print(f"  {tb:14s} kills {k}/{m} non-equivalent"
              f" = {k / m:.3f} [{lo:.3f},{hi:.3f}]")
    lo, hi = statlib.cp_interval(fk, m, 0.95)
    print(f"  {'property set':14s} kills {fk}/{m} non-equivalent"
          f" = {fk / m:.3f} [{lo:.3f},{hi:.3f}]")
    both = sum((kill["union"][int(r[0]) - 1] or r[1] != "-")
               for r in ys if r[2] == "differs")
    print(f"  {'sim + formal':14s} kills {both}/{m} non-equivalent")
    ek = [r[0] for r in eq if kill["union"][int(r[0]) - 1] or r[1] != "-"]
    print(f"  equivalent mutants killed by some check: {len(ek)}"
          f" {' '.join(ek)}")


if __name__ == "__main__":
    main()
