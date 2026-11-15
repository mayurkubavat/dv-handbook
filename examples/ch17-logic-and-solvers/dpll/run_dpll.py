"""run_dpll.py -- what dpll.py does on the chapter's two questions.

    python3 run_dpll.py

First the full adder's question from full_adder.cnf, which unit
propagation answers without a single decision; then the miter of two
adders, where the same procedure makes exactly 4^N - 1 decisions.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
import dimacs  # noqa: E402
import gen  # noqa: E402
from dpll import Dpll  # noqa: E402

NAME = dict(enumerate("a b cin p sum g t cout".split(), start=1))


def text(clause):
    return "(" + " ".join(map(str, clause)) + ")"


print("1. full_adder.cnf with the units 5, 8 and -1")
nvars, clauses = dimacs.read(HERE.parent / "tseitin" / "full_adder.cnf")
s = Dpll(nvars, clauses + [[5], [8], [-1]])
s.log = []
result = s.solve()
for why, what in s.log:
    if why == "conflict":
        print(f"   conflict: every literal of {text(what)} is false")
    else:
        v = abs(what)
        print(f"   {NAME[v]:4s} = {int(what > 0)}   forced by {text(why)}")
print(f"   {'SATISFIABLE' if result else 'UNSATISFIABLE'}: "
      f"{s.decisions} decisions, {s.propagations} propagations, "
      f"{s.conflicts} conflict")
assert result is False and s.decisions == 0

print("2. the miter of two N-bit adders, inputs numbered first")
print("   N  variables  clauses  decisions  conflicts  4^N - 1")
for n in range(2, 8):
    cnf = gen.adder_miter(n)
    s = Dpll(cnf.nvars, cnf.clauses)
    assert s.solve() is False, "the two adders are equal"
    print(f"   {n}  {cnf.nvars:9d}  {len(cnf.clauses):7d}  "
          f"{s.decisions:9,d}  {s.conflicts:9,d}  {4 ** n - 1:7,d}")
    assert s.decisions == 4 ** n - 1 and s.conflicts == 4 ** n
print("   UNSATISFIABLE at every width: the adders are equal;")
print("   decisions = 4^N - 1 in every row: one per node of the tree")
print("   over the 2N input bits")

print("3. the same miter with one gate wrong in the second adder")
for n in (4, 8):
    cnf = gen.adder_miter(n, bug=True)
    s = Dpll(cnf.nvars, cnf.clauses)
    assert s.solve() is True
    m = s.model()
    a = sum((m[i] > 0) << i for i in range(n))
    b = sum((m[n + i] > 0) << i for i in range(n))
    top = n - 1                         # the wrong gate is in this column
    assert (a ^ b) >> top == 1 and (a + b) >> n == 0, "not a difference"
    print(f"   N = {n}: SATISFIABLE after {s.decisions} decisions; "
          f"the adders differ at a = {a}, b = {b}")
