"""uniform.py -- goodness-of-fit tests on fresh draws from the
constrained-random chapter's classes (written by run_draws.sh into
build/), each against the law its constraint asks for: Pearson
chi-square, Kolmogorov-Smirnov, per-bit binomial tests with Bonferroni,
serial-pair independence. Then a control (the same tests on Python's
generator drawing from the asked law, to show the tests reject at their
nominal rate when the law holds) and the power of a bit test. Writes
tbl-ch21-uniform.md, the chapter's table of the tests."""
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent.parent / "ch18-formal-property-"
                       "verification" / "common"))
import statlib as S  # noqa: E402
import tables  # noqa: E402

CLASSES = ("range16", "dist_assign", "dist_divide", "implication",
           "solve_before", "kind")
N, PYSEED, CONTROLS = 2000, 7, 20
C = S.Checks()
LAW = {
    "dist_assign": [0.2 if v in (0, 1, 2, 3, 9) else 0.0
                    for v in range(16)],
    "dist_divide": [0.125 if v < 4 else 0.5 if v == 9 else 0.0
                    for v in range(16)],
    "implication": [1 / 257] * 257,
    "kind": [0.6, 0.3, 0.1],
}


def support(counts, law):
    """Counts and law restricted to the law's support; the count drawn
    outside it, which must be zero."""
    inside = [(c, q) for c, q in zip(counts, law) if q > 0]
    out = sum(c for c, q in zip(counts, law) if q == 0)
    return [c for c, _ in inside], [q for _, q in inside], out


def tests(d):
    """Every test, as (constraint, test, statistic, p). d maps a class
    name to its list of drawn values."""
    out = []
    r = d["range16"]
    top = [v >> 9 for v in r]
    x, df, p = S.pearson(S.hist(top, 64), [1 / 64] * 64)
    out.append(("`v < 16'h8000`", "chi-square, 64 buckets",
                "X2 = %.1f, %d df" % (x, df), p))
    dks, p = S.ks_uniform(r, 32768)
    out.append(("`v < 16'h8000`", "KS against uniform", "D = %.4f" % dks,
                p))
    raw = min(S.normal_sf2((sum(v >> b & 1 for v in r) - len(r) / 2)
                           / math.sqrt(len(r) / 4)) for b in range(15))
    out.append(("`v < 16'h8000`", "15 bit tests, Bonferroni",
                "min raw p %.3g" % raw, min(1.0, 15 * raw)))
    pairs = S.hist([(a >> 3) * 8 + (b >> 3)
                    for a, b in zip(top[:-1:2], top[1::2])], 64)
    x, df, p = S.pearson(pairs, [1 / 64] * 64)
    out.append(("`v < 16'h8000`", "serial pairs, 8 x 8",
                "X2 = %.1f, %d df" % (x, df), p))
    for name, form in (("dist_assign", "`a dist {[0:3] := 1, 9 := 1}`"),
                       ("dist_divide", "`a dist {[0:3] :/ 1, 9 := 1}`")):
        c, q, outside = support(S.hist(d[name], 16), LAW[name])
        x, df, p = S.pearson(c, q)
        out.append((form, "chi-square, 5 values",
                    "X2 = %.1f, %d df" % (x, df), p if not outside else 0.0))
    k = d["kind"]
    x, df, p = S.pearson(S.hist(k, 3), LAW["kind"])
    out.append(("`kind dist {0 :/ 6, 1 :/ 3, 2 :/ 1}`", "chi-square",
                "X2 = %.1f, %d df" % (x, df), p))
    pk = [c / len(k) for c in S.hist(k, 3)]
    tr = S.hist([a * 3 + b for a, b in zip(k[:-1], k[1:])], 9)
    x, _, _ = S.pearson(tr, [pk[i // 3] * pk[i % 3] for i in range(9)])
    out.append(("`kind dist {0 :/ 6, 1 :/ 3, 2 :/ 1}`",
                "consecutive pairs", "X2 = %.1f, 4 df" % x,
                S.chi2_sf(x, 4)))
    im = d["implication"]
    x, df, p = S.pearson(S.hist(im, 257), LAW["implication"])
    out.append(("`s -> v == 0`", "chi-square, 257 solutions",
                "X2 = %.1f, %d df" % (x, df), p))
    s1 = d["solve_before"].count(256)
    n = len(d["solve_before"])
    x, df, p = S.pearson([n - s1, s1], [0.5, 0.5])
    out.append(("`s -> v == 0; solve s before v`", "s = 1 asked 1/2",
                "%d of %d" % (s1, n), p))
    return out


def ptext(p):
    """A p-value for print; one that underflows a float is shown as an
    upper bound."""
    return "%.3g" % p if p > 0 else "< 1e-300"


# ---- the draws ------------------------------------------------------
d, fails = {}, 0
for c in CLASSES:
    lines = (HERE / "build" / ("%s.txt" % c)).read_text().split("\n")
    d[c] = [int(x.split()[2]) for x in lines if x.startswith("D ")]
    fails += sum(int(x.split()[-1]) for x in lines
                 if x.startswith("randomize"))
print("\n== 2. %d fresh draws per class, seed 1 ==" % N)
print("%s with %s" % (sys.argv[1], sys.argv[2]))
C.pin("simulator", sys.argv[1], "Verilator 5.052")
C.pin("draws per class", sorted({len(v) for v in d.values()}), [N])
C.pin("randomize() failures", fails, 0)
res = tests(d)
SHORT = {"`v < 16'h8000`": "range v < 16'h8000",
         "`a dist {[0:3] := 1, 9 := 1}`": "dist := (forms.sv)",
         "`a dist {[0:3] :/ 1, 9 := 1}`": "dist :/ (forms.sv)",
         "`kind dist {0 :/ 6, 1 :/ 3, 2 :/ 1}`": "packet kind 6:3:1",
         "`s -> v == 0`": "s -> v == 0",
         "`s -> v == 0; solve s before v`": "with solve s before v"}
for con, test, stat, p in res:
    print("  %-22s %-25s %-18s %s" % (SHORT[con], test, stat, ptext(p)))
m = len(res)
small = [t for t in res if t[3] < 0.05]
print("  %d tests; below 0.05: %d; below the Bonferroni threshold"
      " 0.05/%d = %.4f: %d" % (m, len(small), m, 0.05 / m,
                      sum(1 for t in res if t[3] < 0.05 / m)))
im1 = d["implication"].count(256)
print("  s = 1 without ordering: %d of %d (1/257 asks %.1f)"
      % (im1, N, N / 257))
sb1 = d["solve_before"].count(256)
print("  s = 1 with solve s before v: %d of %d (the ordering asks %d)"
      % (sb1, N, N // 2))
others = [t for t in res if "solve" not in t[0]]
C.holds("only solve...before rejected at Bonferroni",
        all(t[3] >= 0.05 / m for t in others)
        and all(t[3] < 0.05 / m for t in res if "solve" in t[0]))
C.pin("solve before: s = 1 draws", sb1, 0)
C.pin("implication: s = 1 draws", im1, 10)
C.pin("tests below 0.05", len(small), 1)
C.holds("s = 1 without ordering within the binomial 99.9% range",
        S.binom_cdf(im1, N, 1 / 257) > 0.0005
        and 1 - S.binom_cdf(im1 - 1, N, 1 / 257) > 0.0005)

rows = [[tables.cell(a), tables.cell(b), tables.cell(c), ptext(p)]
        for a, b, c, p in res]
tables.write(HERE / "tbl-ch21-uniform.md",
             ["constraint", "test", "statistic", "p"], rows,
             "Goodness-of-fit tests on %d draws per class, seed 1, %s "
             "with %s {#tbl-ch21-uniform}" % (N, sys.argv[1], sys.argv[2]),
             align=["---", "---", "---", "---:"], grid=True,
             widths=[24, 18, 16, 8])
print("  wrote tbl-ch21-uniform.md")

# ---- the control ----------------------------------------------------
rng = random.Random(PYSEED)


def control(n):
    """The six classes drawn by Python's generator from the law each
    constraint asks for: the tests' behavior when the null holds."""
    def draw(law):
        return rng.choices(range(len(law)), weights=law, k=n)
    return {"range16": [rng.randrange(32768) for _ in range(n)],
            "dist_assign": draw(LAW["dist_assign"]),
            "dist_divide": draw(LAW["dist_divide"]),
            "implication": draw(LAW["implication"]),
            "solve_before": [256 if rng.random() < 0.5
                             else rng.randrange(256) for _ in range(n)],
            "kind": draw(LAW["kind"])}


print("\n== 3. control: Python's generator drawing the asked-for law ==")
allp = []
for _ in range(CONTROLS):
    allp += [t[3] for t in tests(control(N))]
below = sum(1 for p in allp if p < 0.05)
print("  %d samples of %d draws, %d tests each: %d of %d p-values below"
      "\n  0.05 (%.1f expected)" % (CONTROLS, N, m, below, len(allp),
                                   0.05 * len(allp)))
print("  below the Bonferroni threshold: %d"
      % sum(1 for p in allp if p < 0.05 / m))
lo, hi = S.cp_interval(below, len(allp))
C.holds("control rejection rate consistent with 0.05 (CP interval)",
        lo <= 0.05 <= hi)
C.pin("control p-values below 0.05", below, 7)

# ---- power ----------------------------------------------------------
print("\n== 4. power: draws a bit test needs to see a biased bit ==")
print("  a bit set with probability q instead of 1/2; two-sided test at"
      " 0.05;\n  power computed exactly from the binomial law")
za, zb = 1.959964, 1.281552
print("  %5s %s   %s" % ("q", " ".join("n=%-6d" % n for n in
                                       (25, 100, 400, 1600, 6400)),
                         "n for 90%"))
for q in (0.65, 0.55, 0.51):
    pw = []
    for n in (25, 100, 400, 1600, 6400):
        h = za * math.sqrt(n / 4)
        lo_k = math.ceil(n / 2 - h) - 1      # reject when k <= lo_k
        hi_k = math.floor(n / 2 + h) + 1     # or k >= hi_k
        pw.append(S.binom_cdf(lo_k, n, q) + 1 - S.binom_cdf(hi_k - 1, n, q))
    nn = math.ceil(((za * 0.5 + zb * math.sqrt(q * (1 - q)))
                    / (q - 0.5)) ** 2)
    print("  %5.2f %s   %d" % (q, " ".join("%-8.3f" % x for x in pw), nn))
    C.pin("n for 90%% power at q=%.2f" % q, nn,
          {0.65: 113, 0.55: 1047, 0.51: 26265}[q])
C.report()
print("verdict: solve...before drew s = 1 in %d of %d; every other law "
      "held" % (sb1, N))
