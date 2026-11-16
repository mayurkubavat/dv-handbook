"""info.py -- entropy, KL divergence and mutual information as measures
of stimulus: the constrained-random chapter's laws as effective numbers
of values, G = 2 n KL against Pearson's statistic on that chapter's
printed counts (read from its run.out by path), the low bias of plug-in
entropy, and the coverage chapter's FIFO testbench under eight
generators made from its two knobs: spread, reach and the bug trigger
rank them differently, and mutual information says which knob moves
which bin. Writes tbl-ch21-knob.md."""
import math
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent.parent / "ch18-formal-property-"
                       "verification" / "common"))
import statlib as S  # noqa: E402
import dat  # noqa: E402
import tables  # noqa: E402

PYSEED, SEEDS, PERMS = 2026, 250, 200
C = S.Checks()
rng = random.Random(PYSEED)
print("python seed %d" % PYSEED)

print("\n== 1. the constrained-random chapter's laws, in bits ==")
laws = {
    "v uniform 0..255": [1 / 256] * 256,
    "v dist := {1,1,2}": [1 / 412] * 100 + [2 / 412] * 156,
    "v dist :/ {1,1,2}": [0.025] * 10 + [0.25 / 90] * 90
    + [0.5 / 156] * 156,
    "kind 6:3:1": [0.6, 0.3, 0.1],
    "kind uniform 0..2": [1 / 3] * 3,
}
for name, p in laws.items():
    h = S.entropy(p)
    print("  %-18s H %6.3f of %6.3f; 2^H %6.1f; KL to uniform %.4f bits"
          % (name, h, math.log2(len(p)), 2 ** h,
             S.kl(p, [1 / len(p)] * len(p))))
C.near(":= effective values", 2 ** S.entropy(laws["v dist := {1,1,2}"]),
       243.7, 0.05)
C.near(":/ effective values", 2 ** S.entropy(laws["v dist :/ {1,1,2}"]),
       193.5, 0.05)
C.near("kind effective values", 2 ** S.entropy(laws["kind 6:3:1"]), 2.45,
       0.005)

print("\n== 2. G = 2 n KL (nats) is Pearson's statistic's cousin ==")
C7 = HERE.parent.parent / "ch07-constrained-random"
txt = (C7 / "distribution" / "run.out").read_text()
cases = []
for form, law in ((":/", [0.25, 0.25, 0.5]),
                  (":=", [10 / 412, 90 / 412, 312 / 412])):
    m = re.search(r"^dist %s\s+\[0:9\]\s+(\d+)\s+\[10:99\]\s+(\d+)\s+"
                  r"\[100:255\]\s+(\d+)" % form, txt, re.M)
    C.holds("distribution/run.out prints the %s counts" % form, m)
    cases.append(("dist %s" % form, [int(x) for x in m.groups()], law))
kinds = [0, 0, 0]
txt = (C7 / "packet-stream" / "run.out").read_text()
for s in (3, 4):
    m = re.search(r"^seed %d: 64 packets, 0 errors; kinds 0:(\d+) "
                  r"1:(\d+) 2:(\d+)" % s, txt, re.M)
    C.holds("packet-stream/run.out prints seed %d" % s, m)
    kinds = [a + int(b) for a, b in zip(kinds, m.groups())]
cases.append(("packet kinds", kinds, [0.6, 0.3, 0.1]))
for name, cnt, law in cases:
    n = sum(cnt)
    g, df, pg = S.g_test(cnt, law)
    x2, _, px = S.pearson(cnt, law)
    kln = S.kl([c / n for c in cnt], law) * math.log(2)
    print("  %-12s n=%5d KL %.6f nats; G %.3f (p %.3f); X2 %.3f (p %.3f)"
          % (name, n, kln, g, pg, x2, px))
    C.near("%s: G equals 2 n KL" % name, g, 2 * n * kln, 1e-9)
    if n >= 10000:
        C.near("%s: G within 0.05 of X2 at n=%d" % (name, n), g, x2, 0.05)

print("\n== 3. plug-in entropy is biased low on small samples ==")
p = laws["v dist := {1,1,2}"]
true_h = S.entropy(p)
for m in (100, 300, 1000, 3000):
    pl = mm = 0.0
    for _ in range(PERMS):
        h = S.hist(rng.choices(range(256), weights=p, k=m), 256)
        ph = S.entropy([c / m for c in h])
        pl += ph / PERMS
        mm += (ph + (sum(1 for c in h if c) - 1) / (2 * m * math.log(2))) \
            / PERMS
    print("  %5d draws: plug-in %.3f, with the (k-1)/2n correction %.3f;"
          " true %.3f" % (m, pl, mm, true_h))
    if m == 100:
        C.holds("plug-in at 100 draws more than one bit low",
                true_h - pl > 1.0)
        C.pin("plug-in and true entropy at 100 draws",
              ("%.2f" % pl, "%.2f" % true_h), ("6.25", "7.93"))

print("\n== 4. eight generators from the coverage chapter's two knobs ==")
print("%s; %d seeds each; fifo_cg's 29 bins" % (sys.argv[1], SEEDS))
C.pin("simulator", sys.argv[1], "Verilator 5.052")
GENS = [(b, n) for b in ("even", "push") for n in (50, 100, 200, 400)]
data, names = {}, None
for b, n in GENS:
    tag = "%s_%d" % (b, n)
    nm, rows = dat.table([HERE / "build" / ("%s_%d.dat" % (tag, s))
                          for s in range(1, SEEDS + 1)])
    keep = [i for i, x in enumerate(nm) if x.startswith("fifo_cg.")]
    names = [nm[i].split(".", 1)[1] for i in keep]
    trig = [int(x.split()[1]) for x in
            (HERE / "build" / ("%s.trig" % tag)).read_text().split("\n")
            if x]
    data[(b, n)] = ([[r[i] for i in keep] for r in rows], trig)
print("  %-10s %7s %6s %10s %9s" % ("generator", "H bits", "2^H",
                                     "bins/seed", "trigger"))
table, stats = [], {}
for g in GENS:
    rows, trig = data[g]
    tot = [sum(r[i] for r in rows) for i in range(len(names))]
    h = S.entropy([t / sum(tot) for t in tot])
    per = sum(sum(1 for x in r if x) for r in rows) / SEEDS
    tr = sum(trig) / SEEDS
    stats[g] = (h, per, tr)
    print("  %-10s %7.3f %6.1f %10.2f %9.3f" % ("%s %d" % g, h, 2 ** h,
                                                per, tr))
    table.append(["`+bias=%s +n=%d`" % g, "%.3f" % h, "%.1f" % (2 ** h),
                  "%.2f" % per, "%.3f" % tr])


def rank(k):
    return [g for g in sorted(GENS, key=lambda x: -stats[x][k])]


best = [rank(k)[0] for k in range(3)]
top_tr = [g for g in GENS if stats[g][2] == stats[best[2]][2]]
tops = ", ".join("%s %d" % g for g in top_tr)
print("  highest entropy: %s %d; most bins per seed: %s %d;"
      % (*best[0], *best[1]))
print("  highest trigger rate (%.3f): %s" % (stats[best[2]][2], tops))
same = rank(0) == rank(1) == rank(2)
print("  the three measures rank the eight generators the same way: %s"
      % ("yes" if same else "no"))
C.holds("the three rankings differ", not same)
tables.write(HERE / "tbl-ch21-knob.md",
             ["generator", "H (bits)", "effective bins", "bins per seed",
              "trigger rate"], table,
             "Eight generators from the coverage chapter's two knobs, %d "
             "seeds each, %s {#tbl-ch21-knob}" % (SEEDS, sys.argv[1]),
             align=["---", "---:", "---:", "---:", "---:"])
print("  wrote tbl-ch21-knob.md")

print("\n== 5. which knob moves which bin: I(knob; bin hit), bits ==")
units = [(g, r) for g in GENS for r in data[g][0]]


def mi_of(label_of, i, labels=None):
    lab = labels if labels is not None else [label_of(g) for g, _ in units]
    return S.mutual_info(list(zip(lab, [r[i] > 0 for _, r in units])))


res = []
for i, nm in enumerate(names):
    res.append((mi_of(lambda g: g, i), mi_of(lambda g: g[0], i),
                mi_of(lambda g: g[1], i), nm))
res.sort(key=lambda x: (-x[0], x[3]))
base = []
lab = [g for g, _ in units]
for _ in range(PERMS):
    rng.shuffle(lab)
    base.append(max(mi_of(None, i, lab) for i in range(len(names))))
b95 = S.quantile(base, 0.95)
print("  %-24s %9s %7s %7s" % ("bin", "generator", "bias", "n"))
for v, vb, vn, nm in res[:7] + [x for x in res[7:] if x[0] < 1e-12][:3]:
    print("  %-24s %9.3f %7.3f %7.3f" % (nm, v, vb, vn))
print("  permutation baseline, 95th percentile of the largest over the 29"
      " bins:\n  %.4f" % b95)
trig = [t for g in GENS for t in data[g][1]]
it = S.mutual_info(list(zip([g for g in GENS for _ in range(SEEDS)],
                            trig)))
print("  I(generator; trigger) = %.3f bits" % it)
C.pin("permutation baseline", "%.4f" % b95, "0.0075")
fullc = [v for v, _, _, nm in res
         if nm in ("full_cp.full", "occupancy.almost")
         or (nm.startswith("op_x_full.") and nm.endswith("_x_full"))]
C.holds("the six full-FIFO cells carry 0.49 to 0.75 bits, at least 65"
        " times the baseline",
        len(fullc) == 6 and all(0.49 <= v <= 0.75 and v >= 65 * b95
                                for v in fullc))
C.pin("push_x_full: bits from +bias and from +n",
      ("%.3f" % res[0][1], "%.3f" % res[0][2]), ("0.650", "0.027"))
C.near("I(generator; trigger)", it, 0.707, 0.0005)
C.pin("generators that always trigger", top_tr,
      [("push", n) for n in (50, 100, 200, 400)])
C.pin("entropy peak", best[0], ("even", 400))
C.pin("bins-per-seed peak", best[1], ("push", 400))
C.report()
print("verdict: entropy peaks at %s %d, bins per seed at %s %d"
      % (*best[0], *best[1]))
