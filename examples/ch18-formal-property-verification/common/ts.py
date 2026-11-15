"""ts.py -- a transition system read from an AIGER file, for the
chapter's teaching engines.

Three things live here: `Frame`, copies of the model's logic as
clauses; `solve`, one question to the solver of the logic-and-solvers
chapter; and `explicit`, reachability by enumerating every state and
every input, with no solver in it. The engines use the first two. The
third is the referee they are tested against.

A state is written two ways. The engines use a tuple of bits in latch
order; `explicit` packs the same bits into an integer, latch 0 lowest.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CH17 = HERE.parent.parent / "ch17-logic-and-solvers"
sys.path.insert(0, str(CH17 / "common"))
sys.path.insert(0, str(CH17 / "cdcl"))
from aiger import Aig  # noqa: E402
from cdcl import Cdcl  # noqa: E402

QUERIES = [0]                           # solver calls so far


class Frame:
    """CNF copies of the logic. Copy t has its own inputs and ANDs.
    With `link`, the latches of copy t+1 ARE the next-state literals
    of copy t, so a step costs no clauses; the latches of copy 0 are
    free variables, and a caller that wants reset adds `init()`."""

    def __init__(self, aig):
        self.aig = aig
        self.nvars = 1                  # CNF variable 1 is "true"
        self.clauses = [[1]]
        self.frames = []                # copy -> {AIGER variable: literal}

    def fresh(self):
        self.nvars += 1
        return self.nvars

    def lit(self, t, aig_lit):
        """The CNF literal of an AIGER literal in copy t."""
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
        for out, x, y in self.aig.ands:     # g <-> x AND y
            g = self.fresh()
            cur[out >> 1] = g
            a, b = self.lit(t, x), self.lit(t, y)
            self.clauses += [[-g, a], [-g, b], [g, -a, -b]]
        return t

    def latch(self, t, i):
        """Latch i in copy t."""
        return self.lit(t, self.aig.latches[i][0])

    def nxt(self, t, i):
        """The value latch i takes after the step out of copy t."""
        return self.lit(t, self.aig.latches[i][1])

    def init(self, t=0):
        """Unit clauses: the reset value of each latch that has one."""
        return [[self.latch(t, i) if r else -self.latch(t, i)]
                for i, r in sorted(init_values(self.aig).items())]

    def constr(self, t):
        """Unit clauses: the environment's constraints in copy t."""
        return [[self.lit(t, c)] for c in self.aig.constraints]

    def bad(self, t):
        return self.lit(t, self.aig.bads[0])

    def state(self, model, t):
        """The latch values of copy t in a model, as a tuple of bits."""
        return tuple(int(self.latch(t, i) in model)
                     for i in range(len(self.aig.latches)))


def solve(nvars, clauses):
    """One question: a model as a set of true literals, or None."""
    QUERIES[0] += 1
    s = Cdcl(nvars, [list(c) for c in clauses])
    if not s.solve():
        return None
    return set(s.model())


def init_values(aig):
    """Latch index -> 0 or 1 for the latches with a reset value. A
    latch whose reset field is its own literal starts unknown."""
    out = {}
    for i, (lit, _, *reset) in enumerate(aig.latches):
        r = reset[0] if reset else 0
        if r != lit:
            out[i] = r
    return out


# ---- names: a sidecar file, one latch name per line -------------------
def names(path):
    """The latch names of model.aag, from model.names beside it."""
    side = pathlib.Path(path).with_suffix(".names")
    return side.read_text().split()


def fields(bits, latch_names):
    """Bits in latch order -> {register: value}: `count[1]` and
    `count[0]` become one number under `count`."""
    out = {}
    for name, bit in zip(latch_names, bits):
        base, _, index = name.partition("[")
        shift = int(index[:-1]) if index else 0
        out[base] = out.get(base, 0) | (bit << shift)
    return out


def show(bits, latch_names):
    return " ".join(f"{k}={v}" for k, v in fields(bits, latch_names).items())


def unpack(state, n):
    """An integer state of `explicit` as a tuple of n bits."""
    return tuple((state >> i) & 1 for i in range(n))


# ---- the referee: explicit-state search, no solver --------------------
def evaluate(aig, state, inp):
    """One step by evaluating the graph: (next state, constraints
    hold, bad) for an integer state and an integer input."""
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


def initial(aig):
    """Every state that agrees with the reset values."""
    iv = init_values(aig)
    return [s for s in range(1 << len(aig.latches))
            if all((s >> i) & 1 == r for i, r in iv.items())]


def explicit(aig):
    """Breadth-first search from the initial states over every input.
    Returns ({state: step at which it is first reached}, the step at
    which a bad state is first reached or None). The search stops at
    the first bad state."""
    m = len(aig.inputs)
    front = initial(aig)
    seen, depth = {s: 0 for s in front}, 0
    while front:
        new = []
        for s in front:
            for x in range(1 << m):
                nxt, ok, bad = evaluate(aig, s, x)
                if not ok:              # the environment forbids x here
                    continue
                if bad:
                    return seen, depth
                if nxt not in seen:
                    seen[nxt] = depth + 1
                    new.append(nxt)
        front, depth = new, depth + 1
    return seen, None
