"""kind.py -- k-induction on an AIGER model, both halves shown.

    python3 kind.py model.aag [max_k] [--simple]

For k = 0, 1, 2, ... two questions are asked.
  base case: can a bad state be reached in exactly k steps from reset?
  step case: can k good states in a row, starting ANYWHERE, be
             followed by a bad one?
A satisfiable base case is a counterexample. An unsatisfiable step
case, with every base case so far unsatisfiable, is a proof. A
satisfiable step case is a counterexample to induction: the path is
returned, because it is what the proof is stuck on. --simple adds the
constraint that the states of the step case differ pairwise.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "common"))
from ts import Aig, Frame, solve, QUERIES  # noqa: E402


def differ(f, a, b):
    """Clauses: copies a and b differ in at least one latch."""
    out, some = [], []
    for i in range(len(f.aig.latches)):
        x, y, d = f.latch(a, i), f.latch(b, i), f.fresh()
        out += [[-d, x, y], [-d, -x, -y]]       # d implies x != y
        some.append(d)
    return out + [some]


def kind(aig, max_k, simple=False, report=lambda *_: None):
    """(verdict, k, path). The path is the counterexample for "cex",
    the last counterexample to induction for "undetermined"."""
    base = Frame(aig)                   # copy 0 is a reset state
    step = Frame(aig)                   # copy 0 is any state at all
    unique = []                         # the simple-path clauses
    cti = None
    for k in range(max_k + 1):
        t = base.add()
        base.clauses += base.constr(t)
        m = solve(base.nvars, base.clauses + base.init()
                  + [[base.bad(t)]])
        if m is not None:
            report(f"k={k}: base case SAT: a counterexample of {k} steps")
            return "cex", k, [base.state(m, i) for i in range(k + 1)]
        t = step.add()
        step.clauses += step.constr(t)
        if t > 0:
            step.clauses.append([-step.bad(t - 1)])     # good so far
        if simple:
            for j in range(t):
                unique += differ(step, j, t)
        m = solve(step.nvars, step.clauses + unique + [[step.bad(t)]])
        if m is None:
            report(f"k={k}: base case UNSAT, step case UNSAT: proven")
            return "proven", k, None
        cti = [step.state(m, i) for i in range(k + 1)]
        report(f"k={k}: base case UNSAT, step case SAT, from state "
               + "".join(map(str, cti[0])))
    return "undetermined", max_k, cti


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verdict, k, _ = kind(Aig(args[0]),
                         int(args[1]) if len(args) > 1 else 20,
                         "--simple" in sys.argv, print)
    print(f"{verdict} at k = {k}, {QUERIES[0]} queries")
