"""tway.py -- t-way coverage of a configuration space: constructions
that are optimal or nearly so, a greedy array on the architecture
chapter's DMA transfer space with its exclusions as constraints, and
random selection of the same space under two generators. Then the
architecture chapter's own random test, run on Verilator, against this
script's model of its generator (cells of len_x_out per seed).

The space is the factors of that chapter's xfer_cg (length bin,
outcome, error position, slave ready style) plus the channel, for
version 2 of the DMA, whose 16-bit length register cannot express
`over`. Its constraints: a zero-length copy cannot fail; a position
exists only on an error (written "none" otherwise); a one-word copy's
only error position is `first` (the word is first and last at once,
and that chapter's test classifies it as first).
"""
import itertools
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import statlib as S  # noqa: E402
import dat  # noqa: E402

PYSEED, REPS = 2026, 201
C = S.Checks()
rng = random.Random(PYSEED)
print("python seed %d" % PYSEED)

FACTORS = [("len", ["zero", "one", "few", "many", "max"]),
           ("out", ["ok", "rd_err", "wr_err"]),
           ("pos", ["none", "first", "middle", "last"]),
           ("style", ["wait_valid", "ready_first", "random", "w_first"]),
           ("ch", ["0", "1"])]
LEVELS = [len(v) for _, v in FACTORS]
K = len(FACTORS)


def legal(row):
    ln, out, pos = (FACTORS[i][1][row[i]] for i in range(3))
    if ln == "zero" and out != "ok":
        return False
    if (out == "ok") != (pos == "none"):
        return False
    if ln == "one" and pos not in ("none", "first"):
        return False
    return True


ROWS = [r for r in itertools.product(*[range(v) for v in LEVELS])
        if legal(r)]


def tuples_of(row, t):
    return [(ps, tuple(row[p] for p in ps))
            for ps in itertools.combinations(range(len(row)), t)]


def all_tuples(levels, t):
    return {(ps, vs) for ps in itertools.combinations(range(len(levels)), t)
            for vs in itertools.product(*[range(levels[p]) for p in ps])}


def greedy(rows, t):
    """Each new test is the legal row that covers the most uncovered
    t-tuples; ties go to the first such row in the list."""
    unc = set().union(*(tuples_of(r, t) for r in rows))
    out = []
    while unc:
        best = max(rows, key=lambda r: sum(x in unc for x in
                                           tuples_of(r, t)))
        out.append(best)
        unc -= set(tuples_of(best, t))
    return out


def check(rows, levels, t):
    got = set().union(*(tuples_of(r, t) for r in rows))
    return got == all_tuples(levels, t)


# ---- 1. constructions ------------------------------------------------
print("\n== 1. constructions that meet the bound ==")


def binary_pairwise(k):
    """Katona; Kleitman and Spencer: row 0 all zeros; column j, read on
    rows 1..N-1, is a distinct subset of size ceil(N/2). Two such sets
    are incomparable and intersect, which gives the pairs 10, 01, 11;
    row 0 gives 00. N is the least with C(N-1, ceil(N/2)) >= k."""
    n = 2
    while math.comb(n - 1, math.ceil(n / 2)) < k:
        n += 1
    cols = list(itertools.combinations(range(1, n),
                                       math.ceil(n / 2)))[:k]
    return [[int(r in c) for c in cols] for r in range(n)]


for k, want in ((10, 6), (20, 8), (35, 8), (126, 10)):
    rows = binary_pairwise(k)
    ok = check(rows, [2] * k, 2)
    print("  %3d binary factors: %2d rows, every pair covered: %s"
          % (k, len(rows), "yes" if ok else "no"))
    C.pin("binary pairwise rows for k=%d" % k, len(rows), want)
    C.holds("binary construction covers every pair, k=%d" % k, ok)
oa = [[a, b, (a + b) % 3, (a + 2 * b) % 3] for a in range(3)
      for b in range(3)]
ok = check(oa, [3] * 4, 2)
print("  4 three-level factors: rows (a, b, a+b, a+2b) mod 3: %d rows,"
      " every pair: %s" % (len(oa), "yes" if ok else "no"))
C.holds("orthogonal array covers every pair", ok and len(oa) == 9)

# ---- 2. the DMA transfer space ----------------------------------------
print("\n== 2. the DMA transfer space (version 2), constraints built in ==")
print("  factors: " + ", ".join("%s %d" % (n, len(v)) for n, v in FACTORS))
unc6 = [6, 3, 3, 4, 2]
print("  without constraints, as xfer_cg's bins count it (len 6, pos 3):"
      " %d rows;\n  trivial pairwise bound %d"
      % (math.prod(unc6), math.prod(sorted(unc6)[-2:])))
print("  legal rows under the constraints: %d" % len(ROWS))
res = {}
for t in (2, 3):
    tup = set().union(*(tuples_of(r, t) for r in ROWS))
    lower = max(len({vs for ps, vs in tup if ps == pp})
                for pp in itertools.combinations(range(K), t))
    g = greedy(ROWS, t)
    covered = set().union(*(tuples_of(r, t) for r in g))
    res[t] = (tup, g)
    print("  t=%d: %d legal tuples; lower bound %d (largest factor set);"
          " this greedy\n       construction found %d rows, every legal"
          " tuple covered: %s" % (t, len(tup), lower, len(g),
                                  "yes" if covered == tup else "no"))
    C.holds("greedy covers every legal %d-tuple" % t, covered == tup)
    C.holds("greedy rows are legal (t=%d)" % t, all(legal(r) for r in g))
C.pin("legal rows", len(ROWS), 200)
C.pin("legal pairs", len(res[2][0]), 115)
C.pin("greedy size t=2", len(res[2][1]), 23)
C.pin("greedy size t=3", len(res[3][1]), 68)


# ---- 3. random selection, two generators ---------------------------------
def uniform_row():
    return ROWS[rng.randrange(len(ROWS))]


def ch11_dist():
    """Exact probability of each row under the architecture chapter's
    random test, one transfer per test: length by randcase 1:2:4:3
    over 0, 1, [2:15], [16:48]; outcome 6:2:2 when the length is not
    zero; the error word by randcase 1:1:1 over first, last and a
    uniform word; style uniform over four; channel uniform (that test
    runs both channels each round with one style, which changes no
    single-transfer probability)."""
    p = {}
    lens = [(0, 1 / 10)] + [(1, 2 / 10)] + \
        [(n, 4 / 10 / 14) for n in range(2, 16)] + \
        [(n, 3 / 10 / 33) for n in range(16, 49)]
    for n, pn in lens:
        lb = 0 if n == 0 else 1 if n == 1 else 2 if n < 16 else 3
        outs = [(0, 1.0)] if n == 0 else [(0, .6), (1, .2), (2, .2)]
        for o, po in outs:
            if o == 0:
                poss = [(0, 1.0)]
            elif n == 1:
                poss = [(1, 1.0)]
            else:
                poss = [(1, 1 / 3 + 1 / (3 * n)), (3, 1 / 3 + 1 / (3 * n)),
                        (2, (n - 2) / (3 * n))]
            for ps_, pp in poss:
                if pp == 0:
                    continue
                for st in range(4):
                    for c in range(2):
                        r = (lb, o, ps_, st, c)
                        p[r] = p.get(r, 0) + pn * po * pp / 8
    return p


CH11 = ch11_dist()
C.near("generator probabilities sum to one", sum(CH11.values()), 1.0,
       1e-12)
C.holds("generator draws only legal rows", all(legal(r) for r in CH11))
cum, acc = [], 0.0
crow = sorted(CH11)
for r in crow:
    acc += CH11[r]
    cum.append(acc)


def ch11_row():
    import bisect
    return crow[min(len(crow) - 1, bisect.bisect_left(cum, rng.random()
                                                       * acc))]


def tuple_q(dist, t):
    q = {}
    for r, pr in dist.items():
        for x in tuples_of(r, t):
            q[x] = q.get(x, 0) + pr
    return q


UNI = {r: 1 / len(ROWS) for r in ROWS}


def seq_dist():
    """Factor by factor, the way a solver with an ordering draws: the
    length uniform over its five bins, then the outcome uniform over
    those legal for it, the position uniform over those legal for both,
    style and channel uniform."""
    p = {}
    for ln in range(5):
        outs = [o for o in range(3) if any(legal((ln, o, x, 0, 0))
                                           for x in range(4))]
        for o in outs:
            poss = [x for x in range(4) if legal((ln, o, x, 0, 0))]
            for x in poss:
                for st in range(4):
                    for c in range(2):
                        p[(ln, o, x, st, c)] = 1 / 5 / len(outs) \
                            / len(poss) / 8
    return p


SEQ = seq_dist()
C.near("ordered probabilities sum to one", sum(SEQ.values()), 1.0, 1e-12)
srow = sorted(SEQ)
scum, sacc = [], 0.0
for r in srow:
    sacc += SEQ[r]
    scum.append(sacc)


def seq_row():
    import bisect
    return srow[min(len(srow) - 1, bisect.bisect_left(scum, rng.random()
                                                       * sacc))]


def expected(q, tup, n):
    """E[fraction of tup covered by n independent tests] = mean over
    tuples of 1 - (1 - q)^n, q the tuple's probability per test."""
    return sum(1 - (1 - q.get(x, 0)) ** n for x in tup) / len(tup)


def until_full(draw, t, goal, cap=5000):
    left, n = set(goal), 0
    while left and n < cap:
        n += 1
        left -= set(tuples_of(draw(), t))
    return n if not left else None


print("\n== 3. random selection of the same space ==")
CHECK_N = (1, 2, 5, 10, 20, 40, 80, 160, 320)
curves = {}
for t in (2, 3):
    tup, g = res[t]
    qu, qc, qs = tuple_q(UNI, t), tuple_q(CH11, t), tuple_q(SEQ, t)
    reach = {x for x in tup if qc.get(x, 0) > 0}
    full_u = [until_full(uniform_row, t, tup) for _ in range(REPS)]
    full_c = [until_full(ch11_row, t, reach) for _ in range(REPS)]
    full_s = [until_full(seq_row, t, tup) for _ in range(REPS)]
    med_s = S.quantile(full_s, 0.5)
    sim = {n: 0.0 for n in CHECK_N}
    for _ in range(REPS):
        seen, drawn = set(), 0
        for n in CHECK_N:
            while drawn < n:
                seen |= set(tuples_of(uniform_row(), t))
                drawn += 1
            sim[n] += len(seen) / len(tup) / REPS
    un99 = S.union_sum_draws([qu[x] for x in tup], 0.01)
    med_u, med_c = S.quantile(full_u, 0.5), S.quantile(full_c, 0.5)
    print("  t=%d, uniform over the %d legal rows: to cover every legal"
          " tuple,\n       median %d tests (q90 %d); union bound for 99%%:"
          " %d;\n       greedy %d; ratio %.1f"
          % (t, len(ROWS), med_u, S.quantile(full_u, 0.9), un99, len(g),
             med_u / len(g)))
    print("  t=%d, factor by factor (length first): median %d tests"
          " (q90 %d); ratio %.1f"
          % (t, med_s, S.quantile(full_s, 0.9), med_s / len(g)))
    print("  t=%d, the architecture chapter's generator: %d of %d legal"
          " tuples\n       have probability zero (every one with len=max);"
          " the other %d take\n       a median of %d tests"
          % (t, len(tup) - len(reach), len(tup), len(reach), med_c))
    worst = max(abs(sim[n] - expected(qu, tup, n)) for n in CHECK_N)
    print("       formula against %d simulated runs, uniform: largest gap"
          " %.3f" % (REPS, worst))
    C.holds("t=%d formula within 0.01 of simulation" % t, worst <= 0.01)
    C.holds("t=%d: zero-probability tuples are the max ones" % t,
            all(any(p == 0 and v == 4 for p, v in zip(*x))
                for x in tup - reach))
    C.pin("t=%d uniform median to full" % t, med_u, {2: 200, 3: 551}[t])
    C.pin("t=%d ch11 unreachable tuples" % t, len(tup) - len(reach),
          {2: 13, 3: 57}[t])
    C.pin("t=%d ordered median to full" % t, med_s, {2: 89, 3: 378}[t])
    curves[t] = (g, tup, qu, qc, qs)

with open(HERE / "data.tsv", "w") as f:
    f.write("# fraction of legal pairs (t=2) and triples (t=3) of the\n"
            "# DMA transfer space covered after n tests: greedy array,\n"
            "# random uniform over legal rows, random factor by factor,\n"
            "# random under the architecture chapter's generator (the\n"
            "# three random columns by formula)\n")
    f.write("n\tgreedy2\tuniform2\tordered2\tch11gen2"
            "\tgreedy3\tuniform3\tordered3\tch11gen3\n")
    for n in range(1, 201):
        cols = []
        for t in (2, 3):
            g, tup, qu, qc, qs = curves[t]
            gc = set().union(*(tuples_of(r, t) for r in g[:n]))
            cols += [len(gc) / len(tup), expected(qu, tup, n),
                     expected(qs, tup, n), expected(qc, tup, n)]
        f.write("%d\t" % n + "\t".join("%.4f" % c for c in cols) + "\n")
print("  plateau under the architecture chapter's generator: %.3f of"
      " pairs, %.3f\n  of triples, however many tests"
      % (expected(curves[2][3], curves[2][1], 10 ** 6),
         expected(curves[3][3], curves[3][1], 10 ** 6)))

# ---- 4. the architecture chapter's random test on Verilator -----------
if len(sys.argv) > 1:
    seeds, rounds = int(sys.argv[2]), int(sys.argv[3])
    print("\n== 4. %s: that chapter's tb_v2 +test=random +n=%d, seeds"
          " 1..%d ==" % (sys.argv[1], rounds, seeds))
    C.pin("simulator", sys.argv[1], "Verilator 5.052")
    names, rows = dat.table([HERE / "build" / ("r_%d.dat" % s)
                             for s in range(1, seeds + 1)])
    lx = [i for i, n in enumerate(names) if ".len_x_out." in n]
    q2 = {}
    for r, pr in CH11.items():
        q2[(r[0], r[1])] = q2.get((r[0], r[1]), 0) + pr
    lnames = ["zero", "one", "few", "many", "max", "over"]
    onames = ["ok", "rd_err", "wr_err"]
    trans = 2 * rounds
    print("  cell of len_x_out     model P(hit in %d transfers)  measured"
          "  z" % trans)
    zmax, zero_ok = 0.0, True
    for i in lx:
        cell = names[i].split(".")[-1]
        ln, out = cell.split("_x_")
        q = q2.get((lnames.index(ln), onames.index(out)), 0.0)
        pm = 1 - (1 - q) ** trans
        meas = sum(1 for r in rows if r[i]) / seeds
        if pm in (0.0, 1.0):
            zero_ok &= meas == pm
            z = 0.0
        else:
            z = (meas - pm) / math.sqrt(pm * (1 - pm) / seeds)
            zmax = max(zmax, abs(z))
        print("  %-20s %12.3f %27.3f %6.2f" % (cell, pm, meas, z))
    print("  largest |z| over the cells the model gives a chance: %.2f"
          % zmax)
    C.holds("cells of probability zero or one measured so", zero_ok)
    C.holds("every cell within 3.5 sd of the model", zmax < 3.5)
C.report()
print("verdict: greedy %d rows for every legal pair, %d for every triple"
      % (len(res[2][1]), len(res[3][1])))
