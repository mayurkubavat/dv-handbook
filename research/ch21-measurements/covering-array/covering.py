"""covering.py -- t-way coverage of a configuration space: a greedy
covering-array generator against uniform random tests.

The generator is a one-test-at-a-time greedy in the style of AETG
(Cohen, Dalal, Fredman and Patton 1997), written from the published
idea: each new test is the best of M candidates, each candidate built
parameter by parameter in a random order, each value chosen to cover
the most still-uncovered t-tuples with the values fixed so far.
"""
import itertools
import math
import random
import sys

SEED = 2026
rng = random.Random(SEED)
print("python seed %d" % SEED)


def tuples(levels, t):
    """Every t-way interaction: (parameter tuple, value tuple)."""
    out = set()
    for ps in itertools.combinations(range(len(levels)), t):
        for vs in itertools.product(*[range(levels[p]) for p in ps]):
            out.add((ps, vs))
    return out


def covered_by(test, t):
    return {(ps, tuple(test[p] for p in ps))
            for ps in itertools.combinations(range(len(test)), t)}


def greedy(levels, t, cands=30):
    unc = tuples(levels, t)
    k = len(levels)
    rows = []
    while unc:
        best, best_gain = None, -1
        for _ in range(cands):
            order = list(range(k))
            rng.shuffle(order)
            row = [None] * k
            fixed = []
            for p in order:
                scores = []
                for v in range(levels[p]):
                    g = 0
                    # tuples containing p and t-1 already fixed params
                    for others in itertools.combinations(fixed, t - 1):
                        ps = tuple(sorted(others + (p,)))
                        vs = tuple(v if q == p else row[q] for q in ps)
                        g += (ps, vs) in unc
                    scores.append((g, rng.random(), v))
                row[p] = max(scores)[2]
                fixed.append(p)
            gain = len(covered_by(row, t) & unc)
            if gain > best_gain:
                best, best_gain = row, gain
        rows.append(best)
        unc -= covered_by(best, t)
    return rows


def random_until(levels, t, cap=100000):
    unc = tuples(levels, t)
    total = len(unc)
    n = 0
    curve = {}
    while unc and n < cap:
        row = [rng.randrange(v) for v in levels]
        n += 1
        unc -= covered_by(row, t)
        curve[n] = 1 - len(unc) / total
    return n, curve


def expected_frac(levels, t, n):
    """E[fraction of t-tuples covered by n uniform random tests]
    = mean over tuples of 1 - (1 - 1/prod(levels of the tuple))^n."""
    tot = cnt = 0.0
    for ps in itertools.combinations(range(len(levels)), t):
        m = math.prod(levels[p] for p in ps)
        tot += m * (1 - (1 - 1 / m) ** n)
        cnt += m
    return tot / cnt


def union_n(levels, t, delta=0.01):
    """Smallest n with sum over tuples of (1 - 1/m)^n <= delta: random
    tests then cover every t-tuple with probability >= 1 - delta."""
    n = 1
    while True:
        s = 0.0
        for ps in itertools.combinations(range(len(levels)), t):
            m = math.prod(levels[p] for p in ps)
            s += m * (1 - 1 / m) ** n
        if s <= delta:
            return n
        n += 1


SPACES = [
    ("binary k=10", [2] * 10, None),
    ("3-level k=4", [3] * 4, None),
    ("3-level k=13", [3] * 13, None),
    ("DMA config (mixed, 10 params)", [4, 3, 2, 3, 2, 2, 2, 4, 3, 3], None),
]
# Best known sizes, from the published covering-array tables (see the
# research note; binary pairwise from the Katona/Kleitman-Spencer
# formula): CAN(2,10,2)=6, CAN(2,4,3)=9, CAN(2,13,3)=15.
KNOWN = {("binary k=10", 2): 6, ("3-level k=4", 2): 9,
         ("3-level k=13", 2): 15}

print("\n%-30s %2s %7s %6s %6s %6s %8s %8s %8s"
      % ("space", "t", "tuples", "lower", "known", "greedy", "rand med",
         "rand q90", "union99"))
for name, levels, _ in SPACES:
    for t in (2, 3):
        if t == 3 and len(levels) > 10:
            continue
        nt = len(tuples(levels, t))
        lower = math.prod(sorted(levels)[-t:])
        sizes = [len(greedy(levels, t)) for _ in range(3)]
        rn = sorted(random_until(levels, t)[0] for _ in range(41))
        print("%-30s %2d %7d %6d %6s %6d %8d %8d %8d"
              % (name, t, nt, lower, KNOWN.get((name, t), "-"), min(sizes),
                 rn[20], rn[36], union_n(levels, t)))
        sys.stdout.flush()

print("\n== coverage curve, DMA config, t=2 and t=3 ==")
levels = SPACES[3][1]
for t in (2, 3):
    rows = greedy(levels, t)
    nt = len(tuples(levels, t))
    acc = set()
    gcurve = {}
    for i, r in enumerate(rows, 1):
        acc |= covered_by(r, t)
        gcurve[i] = len(acc) / nt
    _, rcurve = random_until(levels, t)
    print(" t=%d greedy size %d" % (t, len(rows)))
    print("   %6s %8s %8s %8s" % ("tests", "greedy", "random", "E[rand]"))
    for n in (1, 2, 4, 8, 16, 24, 32, 48, 64, 100, 150, 200, 300):
        g = gcurve.get(n, 1.0)
        r = rcurve.get(n, 1.0)
        print("   %6d %8.3f %8.3f %8.3f" % (n, g, r,
                                           expected_frac(levels, t, n)))

print("\n== constructions that beat the greedy ==")


def check(rows, levels, t):
    acc = set()
    for r in rows:
        acc |= covered_by(r, t)
    return acc == tuples(levels, t)


# Binary pairwise (Katona 1973; Kleitman and Spencer 1973): row 0 all
# zeros; the columns, read on rows 1..N-1, are distinct subsets of size
# ceil(N/2). Two such sets are incomparable and must intersect, which
# gives the 10, 01 and 11 pairs; row 0 gives 00.
def binary_pairwise(k):
    n = 2
    while math.comb(n - 1, math.ceil(n / 2)) < k:
        n += 1
    cols = list(itertools.combinations(range(1, n), math.ceil(n / 2)))[:k]
    return [[int(r in c) for c in cols] for r in range(n)]


for k in (10, 15, 35, 126):
    rows = binary_pairwise(k)
    print("  binary k=%3d: %d rows, covers every pair: %s"
          % (k, len(rows), check(rows, [2] * k, 2)))
# Orthogonal array OA(9; 4, 3, 2): rows (a, b, a+b, a+2b) mod 3.
oa = [[a, b, (a + b) % 3, (a + 2 * b) % 3] for a in range(3)
      for b in range(3)]
print("  3-level k=4: %d rows (a, b, a+b, a+2b mod 3), covers every pair:"
      " %s" % (len(oa), check(oa, [3] * 4, 2)))
