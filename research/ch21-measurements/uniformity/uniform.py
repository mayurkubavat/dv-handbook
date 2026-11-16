"""uniform.py -- goodness-of-fit tests on draws from Verilator's
constrained randomization (written by run.sh into out/), against the
distribution each constraint asks for: Pearson chi-square, a
Kolmogorov-Smirnov test, bit balance, a serial-pair independence test,
the spread of p-values over twenty seeds, and how many draws a test
needs to see the bias of the pre-fix solver."""
import gzip
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import statlib as S  # noqa: E402


def load(path):
    d = {}
    errs = None
    with gzip.open(path, "rt") as f:
        for line in f:
            t = line.split()
            if t[0] == "D":
                d.setdefault(t[1], []).append(int(t[2]))
            elif t[0] == "ERRORS":
                errs = int(t[1])
    return d, errs


def chi2(counts, probs):
    n = sum(counts)
    x = sum((c - n * p) ** 2 / (n * p) for c, p in zip(counts, probs))
    df = len(probs) - 1
    return x, df, S.chi2_sf(x, df)


def ks_uniform(xs, m):
    """KS statistic of integer draws against the discrete uniform on
    0..m-1, with the asymptotic (continuous) p-value, which is
    conservative for a discrete law."""
    n = len(xs)
    cnt = [0] * m
    for x in xs:
        cnt[x] += 1
    d = 0.0
    c = 0
    for v in range(m):
        c += cnt[v]
        d = max(d, abs(c / n - (v + 1) / m),
                abs((c - cnt[v]) / n - v / m))
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    return d, S.kolmogorov_sf(lam)


def hist(xs, m):
    h = [0] * m
    for x in xs:
        h[x] += 1
    return h


PROBS = {
    "w_values": [1 / 412] * 100 + [2 / 412] * 156,
    "w_ranges": [0.025] * 10 + [0.25 / 90] * 90 + [0.5 / 156] * 156,
    "kind": [0.6, 0.3, 0.1],
    "impl": [1 / 257] * 257,
}


def tests(d):
    """Every test, as (name, statistic text, p-value)."""
    out = []
    r = d["ranged"]
    top = [v >> 9 for v in r]
    x, df, p = chi2(hist(top, 64), [1 / 64] * 64)
    out.append(("ranged: chi2, 64 buckets", "X2=%.1f df=%d" % (x, df), p))
    dks, p = ks_uniform(r, 32768)
    out.append(("ranged: KS vs U{0..32767}", "D=%.4f" % dks, p))
    worst = 1.0
    for b in range(15):
        k = sum(v >> b & 1 for v in r)
        n = len(r)
        z = (k - n / 2) / math.sqrt(n / 4)
        worst = min(worst, math.erfc(abs(z) / math.sqrt(2)))
    # the smallest of 15 p-values is not itself a p-value; Bonferroni
    # makes it one: reject if 15 * min p < alpha
    out.append(("ranged: 15 bit tests, Bonferroni min p",
                "raw min %.3g" % worst, min(1.0, 15 * worst)))
    pairs = [0] * 64
    for a, b in zip(top[:-1:2], top[1::2]):
        pairs[(a >> 3) * 8 + (b >> 3)] += 1
    x, df, p = chi2(pairs, [1 / 64] * 64)
    out.append(("ranged: serial pairs, 8x8", "X2=%.1f df=%d" % (x, df), p))
    for name in ("w_values", "w_ranges"):
        x, df, p = chi2(hist(d[name], 256), PROBS[name])
        out.append(("%s: chi2 per value" % name, "X2=%.1f df=%d" % (x, df),
                    p))
        rng3 = [sum(1 for v in d[name] if v < 10),
                sum(1 for v in d[name] if 10 <= v < 100),
                sum(1 for v in d[name] if v >= 100)]
        pr3 = [sum(PROBS[name][:10]), sum(PROBS[name][10:100]),
               sum(PROBS[name][100:])]
        x, df, p = chi2(rng3, pr3)
        out.append(("%s: chi2 per range %s" % (name, rng3),
                    "X2=%.1f df=%d" % (x, df), p))
    k = d["kind"]
    x, df, p = chi2(hist(k, 3), PROBS["kind"])
    out.append(("kind 6:3:1: chi2 %s" % hist(k, 3), "X2=%.1f df=%d" % (x, df),
                p))
    tr = [0] * 9
    for a, b in zip(k[:-1], k[1:]):
        tr[a * 3 + b] += 1
    pk = [c / len(k) for c in hist(k, 3)]
    x, df, p = chi2(tr, [pk[i // 3] * pk[i % 3] for i in range(9)])
    out.append(("kind: consecutive pairs vs product",
                "X2=%.1f df=%d" % (x, 4), S.chi2_sf(x, 4)))
    x, df, p = chi2(hist(d["impl"], 257), PROBS["impl"])
    s1 = d["impl"].count(256)
    out.append(("impl: joint-uniform chi2, s=1 x%d" % s1,
                "X2=%.1f df=%d" % (x, df), p))
    s1 = d["impl_sb"].count(256)
    n = len(d["impl_sb"])
    x, df, p = chi2([n - s1, s1], [0.5, 0.5])
    out.append(("impl_sb: s=1 asked 1/2, got %d/%d" % (s1, n),
                "X2=%.1f df=%d" % (x, df), p))
    return out


d, errs = load(os.path.join(HERE, "out", "long.txt.gz"))
print("== 1. seed 1, %d draws per class, randomize() failures: %s =="
      % (len(d["ranged"]), errs))
for name, stat, p in tests(d):
    print("  %-46s %-16s p=%.4g" % (name, stat, p))

print("\n== 2. twenty seeds, 500 draws each: p-values per test ==")
table = {}
for s in range(1, 21):
    path = os.path.join(HERE, "out", "short_%d.txt.gz" % s)
    if not os.path.exists(path):
        continue
    ds, _ = load(path)
    for name, _, p in tests(ds):
        table.setdefault(name.split(":")[0] + ":" +
                         name.split(":")[1].split("[")[0].split(",")[0],
                         []).append(p)
for name, ps in table.items():
    print("  %-44s below 0.05: %2d of %d; min %.3g" % (
        name, sum(1 for p in ps if p < 0.05), len(ps), min(ps)))
allp = [p for ps in table.values() for p in ps]
print("  all tests together: %d of %d below 0.05 (%.1f expected if every"
      " null held); Bonferroni threshold 0.05/%d = %.2g, below it: %d"
      % (sum(1 for p in allp if p < 0.05), len(allp), 0.05 * len(allp),
         len(allp), 0.05 / len(allp),
         sum(1 for p in allp if p < 0.05 / len(allp))))



def control(n, rng):
    """The same classes drawn by Python's Mersenne Twister from the law
    each constraint asks for: the tests' behavior when the null holds."""
    def draw(probs):
        return rng.choices(range(len(probs)), weights=probs, k=n)
    sb = [256 if rng.random() < 0.5 else rng.randrange(256)
          for _ in range(n)]
    return {"ranged": [rng.randrange(32768) for _ in range(n)],
            "w_values": draw(PROBS["w_values"]),
            "w_ranges": draw(PROBS["w_ranges"]),
            "kind": draw(PROBS["kind"]), "impl": draw(PROBS["impl"]),
            "impl_sb": sb}


crng = random.Random(7)
print("\n== 2b. control: Python's generator, the asked-for law ==")
for name, stat, p in tests(control(10000, crng)):
    print("  %-46s %-16s p=%.4g" % (name, stat, p))
ctab = {}
for s in range(20):
    for name, _, p in tests(control(500, crng)):
        key = name.split(":")[0] + ":" + \
            name.split(":")[1].split("[")[0].split(",")[0]
        ctab.setdefault(key, []).append(p)
allc = [p for k, ps in ctab.items() if not k.startswith("impl_sb")
        for p in ps]
print("  twenty control samples of 500, all tests but impl_sb: %d of %d"
      " below 0.05" % (sum(1 for p in allc if p < 0.05), len(allc)))
alls = [p for k, ps in table.items() if not k.startswith("impl_sb")
        for p in ps]
print("  the Verilator samples, same tests: %d of %d below 0.05"
      % (sum(1 for p in alls if p < 0.05), len(alls)))

p50 = os.path.join(HERE, "out", "ranged50k.txt.gz")
if os.path.exists(p50):
    d50, e50 = load(p50)
    r = d50["ranged"]
    print("\n== 2c. v < 16'h8000 alone, %d draws, seed 2 ==" % len(r))
    x, df, p = chi2(hist([v >> 9 for v in r], 64), [1 / 64] * 64)
    print("  chi2, 64 buckets: X2=%.1f df=%d p=%.4g" % (x, df, p))
    x, df, p = chi2(hist([v >> 7 for v in r], 256), [1 / 256] * 256)
    print("  chi2, 256 buckets: X2=%.1f df=%d p=%.4g" % (x, df, p))
    dks, p = ks_uniform(r, 32768)
    print("  KS: D=%.4f p=%.4g" % (dks, p))
    for b in range(15):
        k = sum(v >> b & 1 for v in r)
        z = (k - len(r) / 2) / math.sqrt(len(r) / 4)
        print("  bit %2d set in %.4f, p=%.3g" % (
            b, k / len(r), math.erfc(abs(z) / math.sqrt(2))))
    for lo in range(0, 32768, 4096):
        c = sum(1 for v in r if lo <= v < lo + 4096)
        print("  [%5d,%5d): %5d  (%.0f expected)" % (lo, lo + 4096, c,
                                                     len(r) / 8))
    dc, pc = ks_uniform(random.Random(9).choices(range(32768),
                                                 k=len(r)), 32768)
    print("  control, Python generator, same n: KS D=%.4f p=%.4g"
          % (dc, pc))

print("\n== 3. power: draws needed to see a biased bit (Python model) ==")
rng = random.Random(2026)
print("  a bit that is set with probability q instead of 1/2; test:"
      " two-sided binomial z at 0.05; power from 2000 replications")
for q in (0.65, 0.55, 0.51):
    for n in (25, 100, 400, 1600, 6400):
        rej = 0
        for _ in range(2000):
            k = sum(1 for _ in range(n) if rng.random() < q)
            z = (k - n / 2) / math.sqrt(n / 4)
            rej += math.erfc(abs(z) / math.sqrt(2)) < 0.05
        print("  q=%.2f n=%5d power=%.3f" % (q, n, rej / 2000))
    # normal-approximation sample size for 90% power
    za, zb = 1.959964, 1.281552
    nn = ((za * 0.5 + zb * math.sqrt(q * (1 - q))) / (q - 0.5)) ** 2
    print("  q=%.2f: n for 90%% power by formula = %d" % (q, math.ceil(nn)))
