"""bugbound.py -- what N clean seeds say about the per-seed failure
probability: rule of three, exact Clopper-Pearson, a Bayesian bound,
their coverage checked by simulation, and the FIFO's full-at-15 bug
measured on Verilator under three push mixes."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "fifo-log"))
import statlib as S  # noqa: E402
import fifolog  # noqa: E402

SEED = 2026
rng = random.Random(SEED)
print("python seed %d" % SEED)

print("\n== 1. upper 95% bounds on p after n clean tests ==")
print("%7s %10s %10s %10s %10s" % ("n", "3/n", "CP exact", "Bayes U",
                                   "Jeffreys"))
for n in (10, 30, 100, 300, 1000, 3000, 10000):
    cp = S.cp_upper(0, n, 0.05)
    bu = 1 - 0.05 ** (1 / (n + 1))       # Beta(1, n+1) upper quantile
    # Jeffreys prior Beta(1/2,1/2) -> posterior Beta(1/2, n+1/2); its
    # 95% quantile by bisection on the posterior CDF, computed through
    # the binomial identity is not available for half-integer shape,
    # so integrate the density numerically.
    a, b = 0.5, n + 0.5
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)

    def cdf(x, m=4000):
        # substitute x = u^2 to remove the u^-1/2 singularity at 0
        h = math.sqrt(x) / m
        tot = 0.0
        for i in range(m):
            u = (i + 0.5) * h
            t = u * u
            tot += 2 * math.exp(lb + (b - 1) * math.log1p(-t)) * h
        return tot
    lo, hi = 0.0, 10.0 / n
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if cdf(mid) >= 0.95 else (mid, hi)
    print("%7d %10.5f %10.5f %10.5f %10.5f" % (n, 3 / n, cp, bu, lo))

print("\n== 2. does the bound cover the truth? (one-sided 95%) ==")
print("%8s %6s %9s %9s %9s" % ("true p", "n", "cover CP", "cover 3/n",
                               "P(x=0)"))
for p in (0.001, 0.01, 0.05):
    for n in (100, 1000):
        reps = 4000
        c_cp = c_r3 = zero = 0
        for _ in range(reps):
            x = sum(1 for _ in range(n) if rng.random() < p)
            if x == 0:
                zero += 1
                c_r3 += p <= 3 / n
            c_cp += p <= S.cp_upper(x, n, 0.05) if x < 30 else 1
        print("%8.3f %6d %9.3f %9s %9.3f" % (
            p, n, c_cp / reps,
            ("%.3f" % (c_r3 / zero)) if zero else "-", zero / reps))
print("(cover 3/n is over the runs that saw zero failures, the only "
      "runs it applies to)")

print("\n== 3. tests needed for a target bound with zero failures ==")
for target in (0.01, 0.001, 1e-4, 1e-6):
    for conf in (0.95, 0.99):
        n = math.ceil(math.log(1 - conf) / math.log1p(-target))
        print("  p <= %-7g at %.0f%%: n = %d" % (target, 100 * conf, n))

print("\n== 4. the FIFO bug, Verilator 5.052, 200 cycles per seed ==")
even = fifolog.read("even.log")
sweep = fifolog.read("sweep.log")
for name, runs in (("pw=50 pr=50", even),
                   ("pw=30 pr=50", [r for r in sweep if r["pw"] == 30]),
                   ("pw=70 pr=50", [r for r in sweep if r["pw"] == 70])):
    n = len(runs)
    x = sum(r["exposed"] for r in runs)
    lo, hi = S.cp_interval(x, n, 0.95)
    print("  %s: %4d of %4d seeds expose it; p = %.4f, 95%% CP [%.4f,"
          " %.4f]" % (name, x, n, x / n, lo, hi))
    if x == 0:
        print("      zero failures: the 95%% upper bound is %.4f, and "
              "the bug is there" % S.cp_upper(0, n, 0.05))
p = sum(r["exposed"] for r in even) / len(even)
need = math.ceil(math.log(0.01) / math.log1p(-p))
print("  even mix: seeds for a 99%% chance of one exposure: %d" % need)
# clean streaks in seed order versus the geometric law
streaks, cur = [], 0
for r in even:
    if r["exposed"]:
        streaks.append(cur)
        cur = 0
    else:
        cur += 1
print("  clean streaks before an exposure: %d streaks, longest %d, "
      "mean %.2f (geometric mean (1-p)/p = %.2f)"
      % (len(streaks), max(streaks), sum(streaks) / len(streaks),
         (1 - p) / p))
firsts = sorted(r["first"] for r in even if r["exposed"])
print("  cycle of first exposure: min %d, median %d, max %d"
      % (firsts[0], firsts[len(firsts) // 2], firsts[-1]))
# per-cycle hazard is not constant: exposures by 50-cycle window
win = [0] * 4
for f in firsts:
    win[min(3, f // 50)] += 1
print("  first exposures by window [0,50) [50,100) [100,150) [150,200):"
      " %s" % win)

print("\n== 5. the same probabilities from a Markov chain of the FIFO ==")
# State: the monitor's occupancy 0..15 (full is shown at 15, the bug).
# Each cycle draws push and pop independently; a push requested while
# full is the exposure. P(exposed within 200 cycles) is exact.


def p_exposed(pw, pr, cycles=200, depth_full=15):
    dist = [0.0] * (depth_full + 1)
    dist[0] = 1.0
    hit = 0.0
    for _ in range(cycles):
        new = [0.0] * (depth_full + 1)
        for o, m in enumerate(dist):
            if m == 0:
                continue
            for w, pwk in ((1, pw), (0, 1 - pw)):
                for r, prk in ((1, pr), (0, 1 - pr)):
                    q = m * pwk * prk
                    full = o == depth_full
                    if w and full:
                        hit += q
                        continue
                    o2 = o + (w and not full) - (r and o > 0)
                    new[o2] += q
        dist = new
    return hit


for pw in (30, 50, 70):
    ex = p_exposed(pw / 100, 0.5)
    print("  pw=%d pr=50: exact P(exposed in 200 cycles) = %.6f; "
          "clean seeds for a 95%% detection chance: %s"
          % (pw, ex, math.ceil(math.log(0.05) / math.log1p(-ex))
             if 0 < ex < 1 else "-"))
