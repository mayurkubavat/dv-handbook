"""ts.py -- a transition system read from an AIGER file, for the
teaching engines: one copy of the logic as clauses, a query helper on
the chapter-17 solver, and explicit-state reachability as a referee.
"""
import os
import pathlib
import sys

# The repository root: three levels up from this file when it sits in
# research/ch18-measurements/teach/, or the environment's BOOK.
BOOK = pathlib.Path(os.environ.get(
    "BOOK", pathlib.Path(__file__).resolve().parents[3]))
CH17 = BOOK / "examples" / "ch17-logic-and-solvers"
sys.path.insert(0, str(CH17 / "common"))
sys.path.insert(0, str(CH17 / "cdcl"))
from aiger import Aig  # noqa: E402
from cdcl import Cdcl  # noqa: E402

QUERIES = [0]


class Frame:
    """CNF copies of the logic. Frame t has its own inputs, latches
    and ANDs; `link` ties frame t+1's latches to frame t's next-state
    literals with two clauses per latch."""

    def __init__(self, aig):
        self.aig = aig
        self.nvars = 1
        self.clauses = [[1]]
        self.frames = []

    def fresh(self):
        self.nvars += 1
        return self.nvars

    def lit(self, t, aig_lit):
        if aig_lit < 2:
            return 1 if aig_lit else -1
        v = self.frames[t][aig_lit >> 1]
        return -v if aig_lit & 1 else v

    def add(self, link=True):
        t = len(self.frames)
        cur = {}
        self.frames.append(cur)
        for x in self.aig.inputs:
            cur[x >> 1] = self.fresh()
        for lit, nxt, *_ in self.aig.latches:
            if t > 0 and link:
                cur[lit >> 1] = self.lit(t - 1, nxt)
            else:
                cur[lit >> 1] = self.fresh()
        for out, x, y in self.aig.ands:
            g = self.fresh()
            cur[out >> 1] = g
            a, b = self.lit(t, x), self.lit(t, y)
            self.clauses += [[-g, a], [-g, b], [g, -a, -b]]
        return t

    def latch(self, t, i):
        return self.lit(t, self.aig.latches[i][0])

    def nxt(self, t, i):
        return self.lit(t, self.aig.latches[i][1])

    def init(self, t=0):
        """Unit clauses: the reset values of the latches that have one."""
        out = []
        for i, (lit, _, *reset) in enumerate(self.aig.latches):
            r = reset[0] if reset else 0
            if r != lit:
                out.append([self.latch(t, i) if r else -self.latch(t, i)])
        return out

    def constr(self, t):
        return [[self.lit(t, c)] for c in self.aig.constraints]

    def bad(self, t):
        return self.lit(t, self.aig.bads[0])


def solve(nvars, clauses):
    """A model as a set of true literals, or None."""
    QUERIES[0] += 1
    s = Cdcl(nvars, [list(c) for c in clauses])
    if not s.solve():
        return None
    return set(s.model())


def init_values(aig):
    """Latch index -> 0/1 for the latches with a reset value."""
    out = {}
    for i, (lit, _, *reset) in enumerate(aig.latches):
        r = reset[0] if reset else 0
        if r != lit:
            out[i] = r
    return out


# ---- the referee: explicit-state search, no solver --------------------
def evaluate(aig, state, inp):
    val = {0: 0}
    for i, x in enumerate(aig.inputs):
        val[x >> 1] = (inp >> i) & 1
    for i, row in enumerate(aig.latches):
        val[row[0] >> 1] = (state >> i) & 1
    def v(lit):
        return val[lit >> 1] ^ (lit & 1)
    for out, x, y in aig.ands:
        val[out >> 1] = v(x) & v(y)
    nxt = sum(v(row[1]) << i for i, row in enumerate(aig.latches))
    ok = all(v(c) for c in aig.constraints)
    return nxt, ok, bool(v(aig.bads[0]))


def explicit(aig):
    """(reachable set, depth of first bad or None), by breadth-first
    search over every state and input."""
    n, m = len(aig.latches), len(aig.inputs)
    iv = init_values(aig)
    front = [s for s in range(1 << n)
             if all((s >> i) & 1 == r for i, r in iv.items())]
    seen, depth = set(front), 0
    while front:
        new = []
        for s in front:
            for x in range(1 << m):
                nxt, ok, bad = evaluate(aig, s, x)
                if not ok:
                    continue
                if bad:
                    return seen, depth
                if nxt not in seen:
                    seen.add(nxt)
                    new.append(nxt)
        front, depth = new, depth + 1
    return seen, None
