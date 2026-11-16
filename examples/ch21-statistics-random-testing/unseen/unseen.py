"""unseen.py -- how many bins will this generator ever reach? The
species estimators of ecology (Good-Turing, Chao1, Chao2 and Chao2's
extrapolation to one more seed) first on a synthetic bin space whose
truth is known, then on fifo_cg under two generators, from the
seed-by-bin tables the seed-unit and clean-seeds examples write
(counts.tsv, read by path). Each estimate is the median and 10-90%
band over resamples of the seeds, never a single figure. Chao1 is also
computed with every cycle taken as a draw, to show what that unit of
independence hides. Writes data.tsv for the figure."""
import bisect
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402
import dat  # noqa: E402

PYSEED, REPS, ZIPF_REPS = 2026, 200, 300
C = S.Checks()
rng = random.Random(PYSEED)
print("python seed %d; %d resamples per row" % (PYSEED, REPS))

# ---- 1. a synthetic space with a known truth ---------------------------
print("\n== 1. synthetic: 200 bins, p_i proportional to 1/i ==")
TRUE = 200
w = [1 / (i + 1) for i in range(TRUE)]
p = [x / sum(w) for x in w]
cum, c = [], 0.0
for x in p:
    c += x
    cum.append(c)


def draw():
    return min(TRUE - 1, bisect.bisect_left(cum, rng.random() * c))


print("%6s %5s %7s %9s %9s" % ("draws", "seen", "Chao1", "GT miss",
                               "true miss"))
counts, n = [0] * TRUE, 0
for target in (50, 200, 800, 3200):
    while n < target:
        counts[draw()] += 1
        n += 1
    f1 = sum(1 for x in counts if x == 1)
    print("%6d %5d %7.1f %9.4f %9.4f" % (
        n, sum(1 for x in counts if x), S.chao1(counts, n),
        S.good_turing(f1, n), sum(q for q, x in zip(p, counts) if x == 0)))
    if n == 800:
        CH800 = S.chao1(counts, n)
ZMEAN = []
for t in (200, 1600):
    gt = tm = ch = 0.0
    for _ in range(ZIPF_REPS):
        cs = [0] * TRUE
        for _ in range(t):
            cs[draw()] += 1
        gt += S.good_turing(sum(1 for x in cs if x == 1), t) / ZIPF_REPS
        tm += sum(q for q, x in zip(p, cs) if x == 0) / ZIPF_REPS
        ch += S.chao1(cs, t) / ZIPF_REPS
    print("  mean of %d runs of %d draws: Good-Turing %.4f, true missing"
          " mass %.4f;\n  Chao1 %.1f against a truth of %d"
          % (ZIPF_REPS, t, gt, tm, ch, TRUE))
    ZMEAN.append(("%.4f" % gt, "%.4f" % tm, "%.1f" % ch))
    C.near("Good-Turing unbiased at n=%d" % t, gt, tm, 0.01)
    C.holds("Chao1 below the truth on average at n=%d" % t, ch < TRUE)


# ---- 2 and 3. fifo_cg under two generators ----------------------------
def load(path):
    names, rows = dat.read_tsv(path)
    keep = [i for i, nm in enumerate(names) if nm.startswith("fifo_cg.")]
    return [names[i] for i in keep], [[r[i] for i in keep] for r in rows]


def study(label, path, cycles, ts, truth):
    names, rows = load(path)
    k = len(names)
    print("\n== %s ==" % label)
    print("%d seeds of %d cycles; fifo_cg has %d bins, %d reachable on "
          "this RTL" % (len(rows), cycles, k, truth))
    print("%5s %5s %-17s %6s %7s %7s %8s %7s" % (
        "seeds", "seen", "Chao2 med [10,90]", "Q1/Q2", "Chao1cy",
        "Q1/T", "pred new", "P(new)"))
    out = []
    for t in ts:
        so, c1, gt, pn, mn = 0.0, 0.0, 0.0, 0.0, 0.0
        c2s, q1s, q2s = [], 0, 0
        for _ in range(REPS):
            pick = rng.sample(range(len(rows)), t + 1)
            inc, cnt = [0] * k, [0] * k
            for s in pick[:t]:
                for i, x in enumerate(rows[s]):
                    inc[i] += x > 0
                    cnt[i] += x
            e2, q1, q2 = S.chao2(inc, t)
            c2s.append(e2)
            q1s += q1
            q2s += q2
            so += sum(1 for x in inc if x) / REPS
            c1 += S.chao1(cnt, cycles * t) / REPS
            gt += S.good_turing(q1, t) / REPS
            pn += S.chao2_new(inc, t) / REPS
            mn += any(rows[pick[t]][i] and not inc[i]
                      for i in range(k)) / REPS
        med = S.quantile(c2s, 0.5)
        lo, hi = S.quantile(c2s, 0.1), S.quantile(c2s, 0.9)
        print("%5d %5.1f %5.1f [%4.1f,%4.1f] %6s %7.1f %7.3f %8.3f %7.3f"
              % (t, so, med, lo, hi, "%.0f/%.0f" % (q1s / REPS, q2s / REPS),
                 c1, gt, pn, mn))
        out.append((t, so, med, lo, hi, c1, gt, mn))
    return names, rows, out


TS = (1, 2, 4, 8, 16, 32, 64, 128)
n200, r200, even = study("2. fifo_cg, +bias=even +n=200",
                         HERE.parent / "seed-unit" / "counts.tsv", 200,
                         TS, 28)
n30, r30, short = study("3. fifo_cg, +bias=even +n=30",
                        HERE.parent / "clean-seeds" / "counts.tsv", 30,
                        TS, 28)
print("(seen, Chao1cy, Q1/T, pred new and P(new) are means over the "
      "resamples;\n Chao1cy takes every cycle as a draw; Q1/T is "
      "Good-Turing for seeds, the\n expected new bins in one more seed; "
      "pred new is Chao2's extrapolation of\n the same; P(new) is "
      "measured on a held-out seed)")

# all 250 short seeds at once, and the truth from the chain
inc = [sum(1 for r in r30 if r[i]) for i in range(len(n30))]
e2, q1, q2 = S.chao2(inc, len(r30))
seen30 = sum(1 for x in inc if x)
reach15 = F.p_reach(15, 0.5, 0.5, 30)
print("\nall %d seeds of 30 cycles: %d bins seen, Q1 %d, Q2 %d, Chao2 "
      "%.1f; Good-Turing\nQ1/T, new bins expected in the next seed: %.4f"
      % (len(r30), seen30, q1, q2, e2, S.good_turing(q1, len(r30))))
print("the chain's chance that a 30-cycle seed reaches 15 entries, where"
      " the 6\nunseen reachable bins live: %.2g, so %.3f of the %d seeds"
      " are expected\nthere; and %d reachable bins are missing"
      % (reach15, reach15 * len(r30), len(r30), 28 - seen30))
with open(HERE / "data.tsv", "w") as f:
    f.write("# fifo_cg: bins seen and Chao2 (median, 10% and 90% points\n"
            "# over resamples) against seeds, two generators; reachable"
            " 28\n")
    f.write("generator\tseeds\tseen\tchao2_med\tchao2_p10\tchao2_p90\n")
    for tag, rowsx in (("even200", even), ("even30", short)):
        for t, so, med, lo, hi, _, _, _ in rowsx:
            f.write("%s\t%d\t%.2f\t%.2f\t%.2f\t%.2f\n"
                    % (tag, t, so, med, lo, hi))

e4 = dict((r[0], r) for r in even)[4]
s128 = dict((r[0], r) for r in short)[128]
print("\nthe unit of independence: at 4 seeds of 200 cycles, %.1f seen, "
      "Chao1 over\ncycles %.1f, Chao2 over seeds %.1f (median); at 128 "
      "seeds of 30 cycles,\n%.1f seen, Chao1 over cycles %.1f, Chao2 %.1f"
      " (median), reachable 28" % (e4[1], e4[5], e4[2], s128[1], s128[5],
                                   s128[2]))
C.pin("bins seen in 250 short seeds", seen30, 22)
C.near("Chao1 over cycles at 4 even seeds", e4[5], 26.0, 0.05)
C.near("Chao2 median at 4 even seeds", e4[2], 28.1, 0.05)
C.holds("GT tiny while 6 reachable bins are missing",
        S.good_turing(q1, len(r30)) < 0.05 and seen30 == 22)
C.holds("Chao1 over cycles adds under one bin at 4 even seeds",
        e4[5] - e4[1] < 1.0)
C.holds("Chao2 median at 4 even seeds is at least the seen count",
        e4[2] >= e4[1])
C.holds("the chain's reach probability is below 0.01", reach15 < 0.01)
C.near("seeds expected to reach 15 entries", reach15 * len(r30), 0.044,
       0.0005)
# The figures the chapter quotes from sections 1 and 2.
C.pin("Chao2 band at 4 even seeds", ("%.1f" % e4[3], "%.1f" % e4[4]),
      ("22.0", "39.2"))
C.pin("seen at 4 even seeds", "%.1f" % e4[1], "25.7")
C.pin("synthetic means", ZMEAN, [("0.2287", "0.2319", "154.5"),
                                 ("0.0211", "0.0218", "198.8")])
C.pin("synthetic single run, Chao1 at 800 draws", "%.1f" % CH800, "213.3")
C.report()
print("verdict: 250 seeds of 30 cycles saw %d of 28 reachable bins; "
      "Q1/T %.3f" % (seen30, S.good_turing(q1, len(r30))))
