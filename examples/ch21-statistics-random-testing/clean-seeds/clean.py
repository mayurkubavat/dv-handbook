"""clean.py -- what N clean seeds say about the per-seed failure
probability: the exact zero-failure bound against the rule of three
and two Bayesian bounds, how often each covers the truth, the seeds a
target bound costs, and the FIFO under a generator that almost never
reaches its bug, whose clean seeds bound the generator and not the
design. Writes counts.tsv, the seed-by-bin table of the 250 seeds, for
the unseen-bin example."""
import math
import pathlib
import random
import sys
import textwrap

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402
import dat  # noqa: E402

PYSEED, REPS = 2026, 2000
C = S.Checks()
rng = random.Random(PYSEED)
print("python seed %d" % PYSEED)


def jeffreys_upper(n, conf=0.95, m=4000):
    """95% quantile of Beta(1/2, n + 1/2), the posterior after n clean
    tests under the Jeffreys prior, by bisection on a midpoint-rule CDF
    (x = u^2 removes the singularity at zero)."""
    a, b = 0.5, n + 0.5
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)

    def cdf(x):
        h = math.sqrt(x) / m
        return sum(2 * math.exp(lb + (b - 1) * math.log1p(-((i + 0.5) * h)
                                                          ** 2)) * h
                   for i in range(m))
    lo, hi = 0.0, min(1.0, 10.0 / n)
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if cdf(mid) >= conf else (mid, hi)
    return lo


print("\n== 1. one-sided 95% upper bounds on p after n clean seeds ==")
print("%6s %9s %9s %9s %9s" % ("n", "3/n", "exact", "uniform", "Jeffreys"))
for n in (10, 30, 100, 250, 300, 600, 1000, 3000, 10000):
    cp = S.cp_upper(0, n, 0.05)
    bu = 1 - 0.05 ** (1 / (n + 1))      # Beta(1, n + 1) upper quantile
    jf = jeffreys_upper(n)
    print("%6d %9.5f %9.5f %9.5f %9.5f" % (n, 3 / n, cp, bu, jf))
    if n == 600:
        C.near("exact bound after 600", cp, 0.00498, 0.000005)
    if n == 250:
        C.near("exact bound after 250", cp, 0.0119, 0.00005)
    if n >= 300:
        C.rel("rule of three within 1% of exact from n = 300",
              3 / n, cp, 0.01)
        C.rel("uniform-prior bound within 1% of exact from n = 300",
              bu, cp, 0.01)
        C.near("Jeffreys bound about 0.64 of exact", jf / cp, 0.64, 0.01)
print("(exact: 1 - 0.05^(1/n), Clopper-Pearson at zero failures; uniform"
      " and\n Jeffreys: the posterior's 95% point under that prior)")

print("\n== 2. how often the 95%% bound covers the true p (%d trials) =="
      % REPS)
print("%7s %6s %9s %10s %8s" % ("true p", "n", "exact CP", "3/n, x=0",
                                "P(x=0)"))
memo = {}
covered = []


def cp95(x, n):
    if (x, n) not in memo:
        memo[(x, n)] = S.cp_upper(x, n, 0.05)
    return memo[(x, n)]


for p in (0.001, 0.01, 0.05):
    for n in (100, 1000):
        c_cp = c_r3 = zero = 0
        for _ in range(REPS):
            x = sum(1 for _ in range(n) if rng.random() < p)
            c_cp += p <= cp95(x, n)
            if x == 0:
                zero += 1
                c_r3 += p <= 3 / n
        print("%7.3f %6d %9.3f %10s %8.3f" % (
            p, n, c_cp / REPS,
            ("%.3f" % (c_r3 / zero)) if zero else "-", zero / REPS))
        covered.append(c_cp / REPS)
print("(3/n is scored only on the trials with no failure, the only ones"
      " it\n applies to)")
C.pin("smallest coverage of the exact bound", "%.3f" % min(covered), "0.959")
C.holds("the exact bound covers at least 95% everywhere",
        min(covered) >= 0.95)

print("\n== 3. clean seeds needed for a target bound ==")
for target in (0.01, 0.001, 1e-4, 1e-6):
    n95 = S.seeds_to_hit(target, 0.05)
    n99 = S.seeds_to_hit(target, 0.01)
    print("  p <= %-7g  95%%: %8d   99%%: %8d" % (target, n95, n99))
    if target == 0.01:
        C.pin("seeds for 0.01 at 95%", n95, 299)
    if target == 0.001:
        C.pin("seeds for 0.001 at 95%", n95, 2995)
    if target == 1e-6:
        C.pin("seeds for 1e-6 at 95%", n95, 2995731)

print("\n== 4. the FIFO, +bias=even +n=30, %s ==" % sys.argv[1])
C.pin("simulator", sys.argv[1], "Verilator 5.052")
build = HERE / "build"
trig = [int(x.split()[1]) for x in
        (build / "even30.trig").read_text().split("\n") if x]
n = len(trig)
x = sum(trig)
names, rows = dat.table([build / ("even30_%d.dat" % s)
                         for s in range(1, n + 1)])
dat.write_tsv(HERE / "counts.tsv", names, rows, range(1, n + 1),
              "fifo_cg and fill_cg bin counts per seed, +bias=even +n=30,"
              " Verilator 5.052")
ub = S.cp_upper(x, n, 0.05)
exact = F.p_trigger(0.5, 0.5, 30)
print("seeds that pushed while full: %d of %d" % (x, n))
print("95%% upper bound on the per-seed trigger probability: %.4f "
      "(3/n = %.4f)" % (ub, 3 / n))
print("exact chain for this generator: p = %.3g" % exact)
print("  P(all %d seeds clean) = %.3f; seeds for a 95%% chance of one"
      " trigger: %d" % (n, (1 - exact) ** n, S.seeds_to_hit(exact, 0.05)))
print("  the bound is %.0f times the truth, and the bug is in every"
      " seed's RTL" % (ub / exact))
half = math.log(2) / exact
print("  a clean run of n seeds is more likely than not below n = ln 2 / p"
      " = %.0f" % half)
hit = [i for i in range(len(names)) if any(r[i] for r in rows)]
miss = [names[i].split(".", 1)[1] for i in range(len(names))
        if names[i].startswith("fifo_cg.") and i not in hit]
print("fifo_cg bins this generator never hit in %d seeds: %d" % (n,
                                                                len(miss)))
print(textwrap.fill(" ".join(miss), 78, initial_indent="  ",
                    subsequent_indent="  "))
C.pin("triggers at n=30", x, 0)
C.near("bound after 250 clean", ub, 0.0119, 0.00005)
C.near("chain at 30 cycles", exact, 8.45e-5, 0.005e-5)
C.holds("the bound covers the chain's p", ub >= exact)
C.pin("the bound over the truth", round(ub / exact), 141)
C.pin("ln 2 / p", round(half), 8205)
C.pin("seeds for a 95% chance of one trigger",
      S.seeds_to_hit(exact, 0.05), 35462)
C.pin("P(all 250 clean)", "%.3f" % ((1 - exact) ** n), "0.979")
C.report()
print("verdict: %d of %d seeds clean; bound %.4f against a true %.2g"
      % (n - x, n, ub, exact))
