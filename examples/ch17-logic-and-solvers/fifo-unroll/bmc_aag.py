"""bmc_aag.py -- unroll an AIGER model into one CNF per bound.

    python3 bmc_aag.py model.aag [max_bound]

The model is a set of latches, a network of two-input ANDs, one "bad"
literal and optional constraint literals. Frame t gets a fresh copy
of every input and every AND. A latch in frame t+1 is the same CNF
literal as its next-state function in frame t, so the transition
relation costs no clauses beyond the ANDs themselves. Bound k asks:
can the bad literal be true in frame k, with every constraint true in
frames 0 to k? Each bound is solved from nothing by cdcl.py.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "cdcl"))
from aiger import Aig  # noqa: E402
from cdcl import Cdcl  # noqa: E402


class Unroller:
    def __init__(self, aig):
        self.aig = aig
        self.nvars = 1                  # CNF variable 1 is "true"
        self.clauses = [[1]]
        self.frames = []                # frame -> {AIGER variable: literal}

    def fresh(self):
        self.nvars += 1
        return self.nvars

    def lit(self, t, aig_lit):
        """The CNF literal of an AIGER literal in frame t."""
        if aig_lit < 2:
            return 1 if aig_lit else -1
        v = self.frames[t][aig_lit >> 1]
        return -v if aig_lit & 1 else v

    def add_frame(self):
        t = len(self.frames)
        cur = {}
        self.frames.append(cur)
        for x in self.aig.inputs:
            cur[x >> 1] = self.fresh()
        for lit, nxt, *reset in self.aig.latches:
            if t > 0:                   # the wire that fed it last cycle
                cur[lit >> 1] = self.lit(t - 1, nxt)
            elif reset and reset[0] == lit:
                cur[lit >> 1] = self.fresh()        # starts unknown
            else:
                cur[lit >> 1] = 1 if reset and reset[0] else -1
        for out, x, y in self.aig.ands:     # Tseitin: g <-> x AND y
            g = self.fresh()
            cur[out >> 1] = g
            a, b = self.lit(t, x), self.lit(t, y)
            self.clauses += [[-g, a], [-g, b], [g, -a, -b]]
        for c in self.aig.constraints:      # hold in every frame
            self.clauses.append([self.lit(t, c)])
        return t


def bmc(path, max_bound, report=print):
    """Return (bound, unroller, model) of the first counterexample."""
    u = Unroller(Aig(path))
    report(f"model: inputs {len(u.aig.inputs)}, latches "
           f"{len(u.aig.latches)}, ANDs {len(u.aig.ands)}")
    report("bound  variables  clauses  result  decisions  conflicts")
    for k in range(max_bound + 1):
        t = u.add_frame()
        query = u.clauses + [[u.lit(t, u.aig.bads[0])]]
        s = Cdcl(u.nvars, [list(c) for c in query])
        sat = s.solve()
        report(f"{k:5d}  {u.nvars:9d}  {len(query):7d}  "
               f"{'SAT' if sat else 'UNSAT':6s}  {s.decisions:9d}  "
               f"{s.conflicts:9d}")
        if sat:
            model = set(s.model())
            assert all(any(x in model for x in c) for c in query)
            return k, u, model
    report(f"no counterexample up to bound {max_bound}")
    return None, u, None


if __name__ == "__main__":
    bmc(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20)
