"""run_hard.py -- three small families on which the solvers struggle.

    python3 run_hard.py

1. Pigeons: N+1 pigeons, N holes, no two in one hole. Unsatisfiable,
   and every solver here multiplies its work for each added hole.
2. Multipliers: is a*b equal to b*a? Beside the adder miter of the
   same width, to show that the difficulty is the circuit, not the
   size of the formula.
3. Random 3-SAT at a fixed number of variables and a growing number
   of clauses: easy at both ends and hard in the middle.
"""
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).parent
for d in ("common", "dpll", "cdcl"):
    sys.path.insert(0, str(HERE.parent / d))
import gen  # noqa: E402
from cdcl import Cdcl  # noqa: E402
from cdcl_vsids import CdclVsids  # noqa: E402
from dpll import Dpll  # noqa: E402


def run(solver, cnf):
    s = solver(cnf.nvars, [list(c) for c in cnf.clauses])
    return s.solve(), s


print("1. pigeonhole: N+1 pigeons in N holes (unsatisfiable)")
print("   (dpll.py: decisions; the other two: conflicts)")
print("   holes  variables  clauses    dpll   cdcl  cdcl_vsids")
want = {4: (51, 37, 33), 5: (374, 145, 103), 6: (3245, 602, 432),
        7: (32780, 2384, 2019)}
for n, expected in want.items():
    cnf = gen.pigeonhole(n)
    got = []
    for solver in (Dpll, Cdcl, CdclVsids):
        result, s = run(solver, cnf)
        assert result is False, "more pigeons than holes"
        got.append(s.decisions if solver is Dpll else s.conflicts)
    print(f"   {n:5d}  {cnf.nvars:9d}  {len(cnf.clauses):7d}  "
          f"{got[0]:6,d}  {got[1]:5,d}  {got[2]:10,d}")
    assert tuple(got) == expected, (n, got)

print("2. is a*b equal to b*a? beside the adder miter of the same width")
print("   (conflicts of cdcl.py and cdcl_vsids.py; all unsatisfiable)")
print("         adder                         multiplier")
print("   bits  clauses   cdcl  cdcl_vsids    clauses   cdcl  cdcl_vsids")
want = {2: (8, 8), 3: (25, 27), 4: (87, 134), 5: (282, 439),
        6: (1014, 1751), 7: (3655, 7786)}
for n, expected in want.items():
    row, got = f"   {n:4d}", []
    for cnf in (gen.adder_miter(n), gen.multiplier_miter(n)):
        row += f"  {len(cnf.clauses):7d}"
        for solver in (Cdcl, CdclVsids):
            result, s = run(solver, cnf)
            assert result is False
            got.append(s.conflicts)
        row += f"  {got[-2]:5,d}  {got[-1]:10,d}  "
    print(row.rstrip())
    assert tuple(got[2:]) == expected, (n, got)

VARS, RUNS = 60, 30
print(f"3. random 3-SAT, {VARS} variables, {RUNS} formulas per row, "
      f"cdcl_vsids.py")
print("   clauses/variables  clauses  satisfiable  median conflicts"
      "  largest")
sat_column, medians = [], []
for tenth in (30, 34, 38, 42, 46, 50, 54, 58):
    m = VARS * tenth // 10
    sat, conflicts = 0, []
    for seed in range(RUNS):
        cnf = gen.random_3sat(VARS, m, seed)
        result, s = run(CdclVsids, cnf)
        if result:                      # check the model, clause by clause
            model = set(s.model())
            assert all(any(x in model for x in c) for c in cnf.clauses)
        sat += result
        conflicts.append(s.conflicts)
    sat_column.append(sat)
    medians.append(int(statistics.median(conflicts)))
    print(f"   {tenth / 10:17.1f}  {m:7d}  {sat:6d} / {RUNS}  "
          f"{medians[-1]:16d}  {max(conflicts):7d}")
assert sat_column == [30, 30, 28, 22, 6, 3, 0, 0], sat_column
assert medians == [3, 7, 24, 65, 109, 99, 76, 70], medians
print("   the median cost peaks where about half the formulas are "
      "satisfiable")
