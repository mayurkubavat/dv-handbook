"""species.py -- estimating the coverage bins not yet seen, with the
estimators of ecology (Good-Turing, Chao1, Chao2, the Shen-Chao-Lin
extrapolation), on a synthetic bin space whose truth is known and on
the Chapter 1 FIFO's occupancy-by-operation grid run on Verilator."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fifo-log"))
import fifolog  # noqa: E402

SEED = 2026
rng = random.Random(SEED)
print("python seed %d" % SEED)


def chao1(counts, n):
    """Chao1 as written in Boehme's STADS (after Chao 1984), with the
    (n-1)/n factor: S_obs + ((n-1)/n) f1^2 / (2 f2) when f2 > 0, and
    S_obs + ((n-1)/n) f1 (f1-1) / 2 when f2 = 0."""
    f1 = sum(1 for c in counts if c == 1)
    f2 = sum(1 for c in counts if c == 2)
    sobs = sum(1 for c in counts if c > 0)
    if f2 > 0:
        return sobs + (n - 1) / n * f1 * f1 / (2 * f2), f1, f2
    return sobs + (n - 1) / n * f1 * (f1 - 1) / 2, f1, f2


def f0hat(counts, n):
    s, _, _ = chao1(counts, n)
    return s - sum(1 for c in counts if c > 0)


def gt_missing(counts, n):
    """Good-Turing estimate of the probability that the next draw is a
    bin never seen: f1 / n (Good 1953)."""
    return sum(1 for c in counts if c == 1) / n


def new_in_next(counts, n, m):
    """Expected number of new bins in m more draws, f0 * (1 - (1 - f1 /
    (n f0 + f1))^m): the extrapolation of Shen, Chao and Lin (2003) in
    the form STADS and Chao and Colwell (2017, eq. 7c) give."""
    f0 = f0hat(counts, n)
    f1 = sum(1 for c in counts if c == 1)
    if f0 <= 0 or f1 == 0:
        return 0.0
    return f0 * (1 - (1 - f1 / (n * f0 + f1)) ** m)


print("\n== 1. synthetic: 200 bins, p_i proportional to 1/i (Zipf) ==")
S_TRUE = 200
w = [1 / (i + 1) for i in range(S_TRUE)]
tot = sum(w)
p = [x / tot for x in w]
cum = []
c = 0.0
for x in p:
    c += x
    cum.append(c)
import bisect  # noqa: E402
counts = [0] * S_TRUE
draws = []
n = 0
print("%6s %5s %7s %8s %9s %9s %10s %10s" % (
    "n", "S_obs", "Chao1", "f1/f2", "GT miss", "true miss", "new next n",
    "actual"))
checkpoints = [50, 100, 200, 400, 800, 1600, 3200, 6400]
snap = {}
for target in checkpoints + [12800]:
    while n < target:
        i = bisect.bisect_left(cum, rng.random() * c)
        counts[i] += 1
        n += 1
    snap[target] = list(counts)
for t in checkpoints:
    cs = snap[t]
    s1, f1, f2 = chao1(cs, t)
    miss_true = sum(pi for pi, ci in zip(p, cs) if ci == 0)
    pred = new_in_next(cs, t, t)
    actual = (sum(1 for x in snap[2 * t] if x) - sum(1 for x in cs if x))
    print("%6d %5d %7.1f %8s %9.4f %9.4f %10.1f %10d" % (
        t, sum(1 for x in cs if x), s1, "%d/%d" % (f1, f2),
        gt_missing(cs, t), miss_true, pred, actual))

# The Good-Turing estimate averaged over many replications, to show it
# is unbiased for the missing mass where Chao1 is a lower bound.
reps = 300
for t in (200, 1600):
    gt = tm = ch = 0.0
    for _ in range(reps):
        cs = [0] * S_TRUE
        for _ in range(t):
            cs[bisect.bisect_left(cum, rng.random() * c)] += 1
        gt += gt_missing(cs, t)
        tm += sum(pi for pi, ci in zip(p, cs) if ci == 0)
        ch += chao1(cs, t)[0]
    print("  mean over %d replications at n=%d: GT %.4f, true missing "
          "mass %.4f, Chao1 %.1f (truth %d)" % (reps, t, gt / reps,
                                                tm / reps, ch / reps,
                                                S_TRUE))


def chao2(inc, T):
    """Incidence-based Chao2 (Chao 1987), in the form of Chao and Colwell
    (2017), eq. 2b: S_obs + ((T-1)/T) Q1^2 / (2 Q2) when Q2 > 0, and
    S_obs + ((T-1)/T) Q1 (Q1-1) / 2 when Q2 = 0; Q_k is the number of
    bins seen in exactly k sampling units (seeds)."""
    q1 = sum(1 for x in inc if x == 1)
    q2 = sum(1 for x in inc if x == 2)
    sobs = sum(1 for x in inc if x > 0)
    if q2 > 0:
        return sobs + (T - 1) / T * q1 * q1 / (2 * q2), q1, q2
    return sobs + (T - 1) / T * q1 * (q1 - 1) / 2, q1, q2


def fifo_table(runs, label, truth, reps=200):
    print("\n== %s: %d seeds of 200 cycles; reachable bins %d ==" % (
        label, len(runs), truth))
    print("%5s %6s %6s %5s %7s %7s %6s %8s %8s %6s" % (
        "seeds", "S_obs", "Chao2", "med", "Q1/Q2", "Chao1cy", "f1/f2",
        "pred new", "meas new", "P(new)"))
    for T in (1, 2, 4, 8, 16, 32, 64, 128):
        if T >= len(runs):
            break
        so = c2 = c1 = gtn = pn = mn = 0.0
        c2s = []
        q1s = q2s = f1s = f2s = 0
        for _ in range(reps):
            sample = rng.sample(runs, T + 1)
            inc = [0] * 68
            cnt = [0] * 68
            for r in sample[:T]:
                for i, x in enumerate(r["grid"]):
                    inc[i] += x > 0
                    cnt[i] += x
            e2, q1, q2 = chao2(inc, T)
            e1, f1, f2 = chao1(cnt, 200 * T)
            so += sum(1 for x in inc if x)
            c2 += e2
            c2s.append(e2)
            c1 += e1
            q1s += q1
            q2s += q2
            f1s += f1
            f2s += f2
            # predicted new bins in one more seed: the extrapolation with
            # m = 1 in incidence form (Chao and Colwell 2017, eq. 7c),
            # Q0 Q1 / (T Q0 + Q1)
            q0 = e2 - sum(1 for x in inc if x)
            gtn += q0 * q1 / (T * q0 + q1) if q0 > 0 else 0.0
            nxt = sample[T]["grid"]
            new = sum(1 for i in range(68) if nxt[i] and not inc[i])
            mn += new
            pn += new > 0
        m2 = c2 / reps
        med = sorted(c2s)[reps // 2]
        print("%5d %6.1f %6.1f %5.1f %7s %7.1f %6s %8.3f %8.3f %6.3f" % (
            T, so / reps, m2, med,
            "%.0f/%.0f" % (q1s / reps, q2s / reps), c1 / reps,
            "%.0f/%.0f" % (f1s / reps, f2s / reps), gtn / reps, mn / reps,
            pn / reps))


even = fifolog.read("even.log")
sweep = fifolog.read("sweep.log")
fifo_table(even, "2. FIFO grid, pw=50 pr=50, Verilator 5.052", 64)
fifo_table([r for r in sweep if r["pw"] == 30],
           "3. FIFO grid, pw=30 pr=50 (high occupancy almost unreachable)",
           64)
seen30 = sum(1 for i in range(68)
             if any(r["grid"][i] for r in sweep if r["pw"] == 30))
print("  bins seen in all 250 pw=30 seeds: %d (the plan lists 68, the"
      " design can reach 64)" % seen30)
print("  (Chao1cy treats every cycle as an independent draw; Chao2 "
      "treats the seed as the sampling unit; Chao2 is the mean and med "
      "the median over the resamples. pred new is the expected number "
      "of new bins in one more seed; meas new and P(new) are measured "
      "on a held-out "
      "seed.)")
