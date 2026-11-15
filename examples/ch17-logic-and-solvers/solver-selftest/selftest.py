"""selftest.py -- the chapter's solvers against a production solver.

    python3 selftest.py

Three streams of formulas, each given to dpll.py, cdcl.py,
cdcl_vsids.py and z3:

1. small random formulas with clauses of one to four literals, which
   exercise unit clauses, repeated literals and empty variables;
2. random 3-SAT of 30 to 60 variables near the ratio where it is
   hardest, which needs tens to hundreds of conflicts and so exercises
   learning, backjumping and the watch lists;
3. the chapter's own families: pigeonhole, adder and multiplier miters.

All four programs must give the same verdict, every model one of the
chapter's solvers returns is checked clause by clause, and a sample of
the clauses the two learning solvers derive is checked against z3: a
learned clause must follow from the formula. dpll.py is left out of
the formulas that would take it minutes. Needs the z3 Python package;
prints "skipped" without it.
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
import gen  # noqa: E402
from cdcl import Cdcl  # noqa: E402
from cdcl_vsids import CdclVsids  # noqa: E402
from dpll import Dpll  # noqa: E402

LIMIT = 200_000         # a solver that loops fails here; it does not hang
SAMPLE = 20             # learned clauses checked per solver and formula


class Tally:
    def __init__(self):
        self.formulas = self.satisfiable = self.lemmas = 0
        self.most = {Dpll: 0, Cdcl: 0, CdclVsids: 0}


def check(tally, nvars, clauses, solvers, expected=None, lemmas=False):
    """One formula: verdicts, models and (on request) learned clauses."""
    x = [None] + [z3.Bool(f"x{v}") for v in range(1, nvars + 1)]

    def as_z3(clause):
        return z3.Or([x[v] if v > 0 else z3.Not(x[-v]) for v in clause])

    referee = z3.Solver()
    for c in clauses:
        referee.add(as_z3(c))
    verdict = referee.check() == z3.sat
    assert expected in (None, verdict), "z3 against the construction"
    tally.formulas += 1
    tally.satisfiable += verdict
    for solver in solvers:
        s = solver(nvars, [list(c) for c in clauses], LIMIT)
        first = len(s.clauses)          # learned clauses come after these
        assert s.solve() == verdict, (solver.__name__, nvars, clauses)
        tally.most[solver] = max(tally.most[solver], s.conflicts)
        if verdict:
            model = set(s.model())
            assert len(model) == nvars, (solver.__name__, "partial model")
            assert all(any(lit in model for lit in c) for c in clauses), \
                (solver.__name__, nvars, clauses)
        if lemmas and solver is not Dpll:
            for learned in s.clauses[first:first + SAMPLE]:
                referee.push()          # formula and not(learned): unsat
                referee.add(z3.Not(as_z3(learned)))
                assert referee.check() == z3.unsat, \
                    (solver.__name__, "learned clause not implied", learned)
                referee.pop()
                tally.lemmas += 1


def report(title, tally):
    print(title)
    print(f"   {tally.formulas} formulas, {tally.satisfiable} satisfiable, "
          f"{tally.formulas - tally.satisfiable} unsatisfiable")
    print(f"   most conflicts on one formula: dpll {tally.most[Dpll]:,d}, "
          f"cdcl {tally.most[Cdcl]:,d}, cdcl_vsids "
          f"{tally.most[CdclVsids]:,d}")


ALL, LEARNING = (Dpll, Cdcl, CdclVsids), (Cdcl, CdclVsids)
total = Tally()

small, rng = Tally(), random.Random(1)
for trial in range(1500):
    n = 1 + int(rng.random() * 25)
    m = 1 + int(rng.random() * (5.5 * n + 2))
    clauses = [[(1 + int(rng.random() * n)) * (1 if rng.random() < 0.5
                                               else -1)
                for _ in range(1 + int(rng.random() * 4))]
               for _ in range(m)]
    check(small, n, clauses, ALL)
report("1. small formulas, up to 25 variables, clauses of 1 to 4 literals",
       small)

dense, rng = Tally(), random.Random(2)
for trial in range(240):
    n = 30 + int(rng.random() * 31)
    m = int(n * (4.0 + 0.6 * rng.random()))
    cnf = gen.random_3sat(n, m, 1000 + trial)
    check(dense, n, cnf.clauses, ALL if n <= 40 else LEARNING,
          lemmas=trial % 4 == 0)
report("2. random 3-SAT, 30 to 60 variables, 4.0 to 4.6 clauses for each",
       dense)

family = Tally()
for n in range(2, 7):
    for cnf, expected, solvers in (
            (gen.pigeonhole(n), False, ALL if n <= 5 else LEARNING),
            (gen.adder_miter(n), False, ALL),
            (gen.adder_miter(n, bug=True), True, ALL),
            (gen.multiplier_miter(n), False, ALL if n <= 4 else LEARNING)):
        check(family, cnf.nvars, cnf.clauses, solvers, expected, lemmas=True)
report("3. pigeonhole, adder miters with and without the bug, multiplier "
       "miters,\n   2 to 6 holes or bits", family)

count = small.formulas + dense.formulas + family.formulas
lemmas = dense.lemmas + family.lemmas
assert max(dense.most[Cdcl], dense.most[CdclVsids]) >= 100, "too easy"
print(f"{count} formulas: dpll.py, cdcl.py and cdcl_vsids.py agree with z3 "
      "on every one")
print("every model satisfies every clause and assigns every variable")
print(f"{lemmas} learned clauses checked: each follows from its formula")
