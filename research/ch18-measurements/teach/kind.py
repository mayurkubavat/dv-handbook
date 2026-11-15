"""kind.py -- k-induction on an AIGER model, showing both halves.

    python3 kind.py model.aag [max_k] [--simple]

For k = 0, 1, 2, ...: the base case asks whether a bad state is k
steps from reset; the step case asks whether k good states in a row,
starting ANYWHERE, can be followed by a bad one. Step unsatisfiable
with every base so far unsatisfiable is a proof. A satisfiable step
is a counterexample to induction: it is printed, because it is the
state the proof is stuck on. --simple adds the constraint that the
states of the step case are pairwise different.
"""
import sys
from ts import Aig, Frame, solve, QUERIES


def state_of(f, model, t):
    return tuple(int(f.latch(t, i) in model)
                 for i in range(len(f.aig.latches)))


def differ(f, a, b):
    """Clauses: the latches of frames a and b differ somewhere."""
    out, big = [], []
    for i in range(len(f.aig.latches)):
        x, y, d = f.latch(a, i), f.latch(b, i), f.fresh()
        out += [[-d, x, y], [-d, -x, -y]]      # d -> x != y
        big.append(d)
    return out + [big]


def kind(path, max_k, simple, report=print):
    return kind_aig(Aig(path), max_k, simple, report)


def kind_aig(aig, max_k, simple, report=lambda *_: None):
    base = Frame(aig)                   # frame 0 is the reset state
    step = Frame(aig)                   # frame 0 is any state at all
    extra = []                          # simple-path clauses
    for k in range(max_k + 1):
        t = base.add()
        base.clauses += base.constr(t)
        q = base.clauses + base.init() + [[base.bad(t)]]
        m = solve(base.nvars, q)
        if m is not None:
            report(f"k={k}: base case SAT: counterexample of depth {k}")
            return "cex", k, [state_of(base, m, i) for i in range(k + 1)]
        t = step.add()
        step.clauses += step.constr(t)
        if t > 0:
            step.clauses.append([-step.bad(t - 1)])
        if simple:
            for j in range(t):
                extra += differ(step, j, t)
        m = solve(step.nvars, step.clauses + extra + [[step.bad(t)]])
        if m is None:
            report(f"k={k}: base case UNSAT, step case UNSAT: proven")
            return "proven", k, None
        cti = [state_of(step, m, i) for i in range(k + 1)]
        report(f"k={k}: base case UNSAT, step case SAT: "
               f"induction fails from state {cti[0]}")
    return "undetermined", max_k, cti


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    r = kind(args[0], int(args[1]) if len(args) > 1 else 20,
             "--simple" in sys.argv)
    print(r[0], "k =", r[1], "queries", QUERIES[0])
