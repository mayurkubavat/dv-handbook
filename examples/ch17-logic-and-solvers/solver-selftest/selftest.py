"""selftest.py -- the chapter's solvers against a production solver.

    python3 selftest.py

Three thousand small random formulas, each given to dpll.py, cdcl.py,
cdcl_vsids.py and z3. All four must give the same verdict, and every
model one of the chapter's solvers returns is checked clause by
clause. Needs the z3 Python package; prints "skipped" without it.
"""
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).parent
for d in ("common", "dpll", "cdcl"):
    sys.path.insert(0, str(HERE.parent / d))
try:
    import z3
except ImportError:
    print("skipped: the z3 Python package is not installed")
    sys.exit(0)
from cdcl import Cdcl  # noqa: E402
from cdcl_vsids import CdclVsids  # noqa: E402
from dpll import Dpll  # noqa: E402

TRIALS = 3000


def referee(nvars, clauses):
    x = [None] + [z3.Bool(f"x{v}") for v in range(1, nvars + 1)]
    s = z3.Solver()
    for c in clauses:
        s.add(z3.Or([x[v] if v > 0 else z3.Not(x[-v]) for v in c]))
    return s.check() == z3.sat


rng = random.Random(1)
satisfiable = 0
for trial in range(TRIALS):
    n = 1 + int(rng.random() * 25)
    m = 1 + int(rng.random() * (5.5 * n + 2))
    clauses = [[(1 + int(rng.random() * n)) * (1 if rng.random() < 0.5
                                               else -1)
                for _ in range(1 + int(rng.random() * 4))]
               for _ in range(m)]
    expected = referee(n, clauses)
    satisfiable += expected
    for solver in (Dpll, Cdcl, CdclVsids):
        s = solver(n, [list(c) for c in clauses])
        assert s.solve() == expected, (solver.__name__, clauses)
        if expected:
            model = set(s.model())
            assert all(any(x in model for x in c) for c in clauses), \
                (solver.__name__, clauses)
print(f"{TRIALS} random formulas of up to 25 variables:")
print("dpll.py, cdcl.py and cdcl_vsids.py agree with z3 on every one")
print(f"{satisfiable} satisfiable, each model checked clause by clause; "
      f"{TRIALS - satisfiable} unsatisfiable")
