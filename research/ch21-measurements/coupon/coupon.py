"""coupon.py -- how many draws until every bin is hit: the formulas
against simulation, for equal and unequal bin probabilities, and then
against the Chapter 1 FIFO run on Verilator, where the draws are not
independent. Writes nothing; run it and read stdout (saved as run.out).
"""
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
TRIALS = 4000
print("python seed %d, %d trials per simulated row" % (SEED, TRIALS))


def simulate(p, trials=TRIALS):
    """Draw from p until every bin with p_i > 0 is hit; return the list
    of draw counts."""
    k = len(p)
    cum = []
    c = 0.0
    for q in p:
        c += q
        cum.append(c)
    import bisect
    out = []
    for _ in range(trials):
        seen = [False] * k
        left = k
        t = 0
        while left:
            t += 1
            i = bisect.bisect_left(cum, rng.random() * c)
            if not seen[i]:
                seen[i] = True
                left -= 1
        out.append(t)
    return out


def quant(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def row(name, p):
    sims = simulate(p)
    mean = sum(sims) / len(sims)
    sd = math.sqrt(sum((x - mean) ** 2 for x in sims) / (len(sims) - 1))
    e = S.coupon_expect(p)
    k = len(p)
    naive = S.coupon_expect_equal(k)
    n99 = S.draws_for_all(p, 0.01)
    ub = S.union_bound_draws(p, 0.01)
    print("%-34s k=%4d E[T]=%9.1f sim=%9.1f (se %5.1f) equal-p=%8.1f"
          % (name, k, e, mean, sd / math.sqrt(len(sims)), naive))
    ex = (" exact=%d" % S.draws_for_all(p, 0.01, S.coupon_cdf_exact)
          if k <= 12 else "")
    print("%-34s        n99 Poisson=%7d sim q99=%7d union=%7d%s"
          % ("", n99, quant(sims, 0.99), ub, ex))


print("\n== 1. equal probabilities: E[T] = k H_k ==")
for k in (8, 64, 256):
    row("equal, k=%d" % k, [1.0 / k] * k)

print("\n== 2. the packet kind dist {0:/6, 1:/3, 2:/1} ==")
p = [0.6, 0.3, 0.1]
row("kind 0/1/2", p)
for n in (10, 20, 30, 44, 50):
    print("   P(all three kinds within %2d packets): exact %.4f"
          "  Poisson %.4f" % (n, S.coupon_cdf_exact(p, n),
                             S.coupon_cdf_poisson(p, n)))
print("   the Ch 7 run is 64 packets: P(kind 2 never) = 0.9^64 = %.5f"
      % 0.9 ** 64)

print("\n== 3. every value of an 8-bit v under the Ch 7 dist forms ==")
assign = [1 / 412] * 10 + [1 / 412] * 90 + [2 / 412] * 156
divide = [0.25 / 10] * 10 + [0.25 / 90] * 90 + [0.5 / 156] * 156
row("v dist := {1,1,2}", assign)
row("v dist :/ {1,1,2}", divide)
row("v uniform 0..255", [1 / 256] * 256)

print("\n== 4. the FIFO grid (occupancy x op), Verilator 5.052 ==")
runs = fifolog.read("even.log")
long = fifolog.read("long.log")[0]
nb = 68
reach = [i for i in range(nb) if any(r["grid"][i] for r in runs)]
print("seeds %d, 200 cycles each; bins hit in some seed: %d of %d"
      % (len(runs), len(reach), nb))
tot = sum(long["grid"])
pc = [long["grid"][i] / tot for i in range(nb)]
print("long run: %d cycles; bins hit: %d" % (tot, sum(1 for x in pc if x)))
# per-run hit probability measured over seeds, and the prediction an
# independent-cycles model makes from the long run's per-cycle rates
print("%-14s %9s %10s %10s" % ("bin", "p/cycle", "P(run) iid",
                              "P(run) meas"))
pred, meas = [], []
for i in reach:
    pi = sum(1 for r in runs if r["grid"][i]) / len(runs)
    pr = 1 - (1 - pc[i]) ** 200
    pred.append(pr)
    meas.append(pi)
rare = sorted(range(len(reach)), key=lambda j: meas[j])[:8]
for j in rare:
    i = reach[j]
    print("%-14s %9.5f %10.4f %10.4f" % (fifolog.bin_name(i), pc[i],
                                         pred[j], meas[j]))
over = sum(1 for a, b in zip(pred, meas) if a > b)
print("bins where the iid model over-predicts the run hit rate: %d of %d"
      % (over, len(reach)))
# seeds until all reachable bins are hit, measured by resampling the
# 1000 seeds in random order, against the seed-level prediction
need = []
for _ in range(2000):
    order = list(range(len(runs)))
    rng.shuffle(order)
    left = set(reach)
    for t, s in enumerate(order, 1):
        g = runs[s]["grid"]
        left -= {i for i in left if g[i]}
        if not left:
            break
    need.append(t)
# seed-level model: bins independent, each hit by a seed w.p. meas
pdict = meas


def cdf_seeds(n):
    prod = 1.0
    for q in pdict:
        prod *= 1 - (1 - q) ** n
    return prod


n99 = next(n for n in range(1, 10000) if cdf_seeds(n) >= 0.99)
n50 = next(n for n in range(1, 10000) if cdf_seeds(n) >= 0.5)
print("seeds to hit all %d reachable bins: resampled median %d, q99 %d"
      % (len(reach), quant(need, 0.5), quant(need, 0.99)))
print("seed-level model (bins independent): median %d, n99 %d"
      % (n50, n99))
print("seed-level union bound: n = %d seeds"
      % max(math.ceil(math.log(len(meas) / 0.01) / -math.log1p(-q))
            for q in meas if q < 1))
pcr = [pc[i] for i in reach]
c99 = S.draws_for_all([q / sum(pcr) for q in pcr], 0.01)
print("cycle-level iid model: n99 = %d cycles = %.1f seeds of 200"
      % (c99, c99 / 200))
