"""info.py -- entropy, KL divergence and mutual information as measures
of stimulus quality: the Chapter 7 distributions, the link between KL
divergence and the goodness-of-fit statistic, and which FIFO bins a
push-rate knob actually controls (Verilator 5.052 runs)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "fifo-log"))
import statlib as S  # noqa: E402
import fifolog  # noqa: E402

print("== 1. entropy of the Chapter 7 distributions (bits) ==")
dists = {
    "v uniform 0..255": [1 / 256] * 256,
    "v dist := {1,1,2}": [1 / 412] * 100 + [2 / 412] * 156,
    "v dist :/ {1,1,2}": [0.025] * 10 + [0.25 / 90] * 90 + [0.5 / 156] * 156,
    "kind 6:3:1": [0.6, 0.3, 0.1],
    "kind uniform 0..2": [1 / 3] * 3,
}
for name, p in dists.items():
    h = S.entropy(p)
    print("  %-20s H=%6.3f  max=%6.3f  2^H=%7.1f  KL to uniform=%.4f"
          % (name, h, math.log2(len(p)), 2 ** h,
             S.kl(p, [1 / len(p)] * len(p))))

print("\n== 2. KL divergence is the G-test: G = 2 n KL (nats) ~ chi2 ==")
counts = [6076, 2940, 984]          # kind, 10000 draws, Verilator seed 1
n = sum(counts)
emp = [c / n for c in counts]
target = [0.6, 0.3, 0.1]
kl_nats = S.kl(emp, target) * math.log(2)
g = 2 * n * kl_nats
x2 = sum((c - n * t) ** 2 / (n * t) for c, t in zip(counts, target))
print("  counts %s: KL=%.6f bits, G=%.3f p=%.3f; Pearson X2=%.3f p=%.3f"
      % (counts, kl_nats / math.log(2), g, S.chi2_sf(g, 2), x2,
         S.chi2_sf(x2, 2)))

print("\n== 3. plug-in entropy is biased low on small samples ==")
import random  # noqa: E402
rng = random.Random(2026)
p = dists["v dist := {1,1,2}"]
true_h = S.entropy(p)
for m in (100, 300, 1000, 3000, 10000):
    pl = mm = 0.0
    reps = 200
    for _ in range(reps):
        xs = rng.choices(range(256), weights=p, k=m)
        h = [0] * 256
        for x in xs:
            h[x] += 1
        ph = S.entropy([c / m for c in h])
        k = sum(1 for c in h if c)
        pl += ph
        mm += ph + (k - 1) / (2 * m * math.log(2))   # Miller-Madow
    print("  n=%5d plug-in %.3f  Miller-Madow %.3f  true %.3f"
          % (m, pl / reps, mm / reps, true_h))

print("\n== 4. the push-rate knob and the FIFO bins (Verilator 5.052) ==")
runs = fifolog.read("sweep.log")
knobs = sorted({r["pw"] for r in runs})
print("  knob pw in %s, pop 50, 250 seeds each, 200 cycles" % knobs)
print("  %4s %9s %9s %8s %9s" % ("pw", "H(bins)", "2^H", "bins/run",
                                 "exposed"))
for k in knobs:
    rs = [r for r in runs if r["pw"] == k]
    tot = [sum(r["grid"][i] for r in rs) for i in range(68)]
    s = sum(tot)
    h = S.entropy([t / s for t in tot])
    per = sum(sum(1 for x in r["grid"] if x) for r in rs) / len(rs)
    ex = sum(r["exposed"] for r in rs) / len(rs)
    print("  %4d %9.3f %9.1f %8.1f %9.3f" % (k, h, 2 ** h, per, ex))


def mi(pairs):
    """Plug-in mutual information (bits) of a list of (a, b) pairs."""
    n = len(pairs)
    ja, jb, jab = {}, {}, {}
    for a, b in pairs:
        ja[a] = ja.get(a, 0) + 1
        jb[b] = jb.get(b, 0) + 1
        jab[(a, b)] = jab.get((a, b), 0) + 1
    return sum(c / n * math.log2(c * n / (ja[a] * jb[b]))
               for (a, b), c in jab.items())


res = []
for i in range(68):
    pairs = [(r["pw"], r["grid"][i] > 0) for r in runs]
    res.append((mi(pairs), fifolog.bin_name(i),
                [sum(1 for r in runs if r["pw"] == k and r["grid"][i])
                 / 250 for k in knobs]))
res.sort(reverse=True)
print("  I(knob; bin hit in a run), bits, max possible 1.0 for a binary"
      " outcome:")
for v, name, rates in res[:6] + res[-6:]:
    print("    %-12s %.3f   hit rate by pw %s" % (
        name, v, " ".join("%.2f" % x for x in rates)))
pairs = [(r["pw"], r["exposed"]) for r in runs]
print("  I(knob; exposed) = %.3f bits" % mi(pairs))
# permutation baseline: the plug-in MI of a knob that does nothing
rng2 = random.Random(1)
base = []
for _ in range(200):
    lab = [r["pw"] for r in runs]
    rng2.shuffle(lab)
    base.append(max(mi(list(zip(lab, [r["grid"][i] > 0 for r in runs])))
                for i in range(0, 68, 9)))
base.sort()
print("  permutation baseline (knob shuffled), 95th pct of max over 8"
      " bins: %.4f bits" % base[189])
