"""run_cdcl.py -- what clause learning changes, measured.

    python3 run_cdcl.py

Part 1 prints one conflict of cdcl.py on the 3-bit adder miter in
full: the trail at the conflict's decision level, each resolution
step of the analysis, the learned clause and the backjump. Part 2 is
the table: the same instances as run_dpll.py under dpll.py, cdcl.py
(same decision order, with learning) and cdcl_vsids.py (learning and
an activity heuristic).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "dpll"))
import gen  # noqa: E402
from cdcl import Cdcl  # noqa: E402
from cdcl_vsids import CdclVsids  # noqa: E402
from dpll import Dpll  # noqa: E402

SHOWN = 20                              # which conflict part 1 prints


def text(clause):
    return "(" + " ".join(map(str, clause)) + ")"


def resolve(c1, c2, var):
    """The resolvent of two clauses on a variable they disagree on."""
    assert (var in c1 and -var in c2) or (-var in c1 and var in c2)
    return sorted({x for x in c1 + c2 if abs(x) != var}, key=abs)


class Explain(Cdcl):
    """cdcl.py, printing its analysis of one chosen conflict."""
    origin = {}                         # learned clause -> its conflict

    def analyze(self, conflict):
        if self.conflicts != SHOWN:
            learned, back = super().analyze(conflict)
            self.origin[frozenset(learned)] = self.conflicts
            return learned, back
        here = len(self.trail_lim)
        level = [x for x in self.trail if self.level[abs(x)] == here]
        print(f"   conflict {SHOWN}, at decision level {here}; the "
              f"trail at this level:")
        for lit in level:
            why = self.reason[abs(lit)]
            if why is None:
                print(f"     {lit:4d}   decision")
                continue
            note = self.origin.get(frozenset(why))
            print(f"     {lit:4d}   {text(sorted(why, key=abs))}"
                  + (f"   learned at conflict {note}" if note else ""))
        print(f"   falsified clause: {text(sorted(conflict, key=abs))}")
        # The analysis again, as explicit resolution steps: resolve on
        # the most recently assigned literal until one is left here.
        clause = sorted(conflict, key=abs)
        for lit in reversed(level):
            at_level = [x for x in clause if self.level[abs(x)] == here]
            if len(at_level) == 1:
                break
            if -lit in clause:
                why = sorted(self.reason[abs(lit)], key=abs)
                clause = resolve(clause, why, abs(lit))
                print(f"   resolve on {abs(lit):2d} with {text(why)}:"
                      f" {text(clause)}")
        learned, back = super().analyze(conflict)
        assert sorted(learned, key=abs) == clause, "the two analyses differ"
        print(f"   learned clause: {text(clause)}; first unique "
              f"implication point: {-learned[0]}")
        print("   levels of its other literals: " + ", ".join(
            f"{x} at {self.level[abs(x)]}" for x in learned[1:]))
        print(f"   backjump to level {back}, where the clause forces "
              f"{learned[0]}")
        self.shown = (clause, back)
        return learned, back


def run(solver, cnf, limit=None):
    s = solver(cnf.nvars, [list(c) for c in cnf.clauses], limit)
    return s.solve(), s


print("1. one conflict of cdcl.py on the 3-bit adder miter")
cnf = gen.adder_miter(3)
print("   variables: a0 a1 a2 = 1 2 3; b0 b1 b2 = 4 5 6; gates:")
for g in (13, 27, 14, 15, 28, 29, 37):
    op, *ins = cnf.defs[g]
    print(f"     {g} = {op}({', '.join(map(str, ins))})")
result, s = run(Explain, cnf)
assert result is False and s.shown == ([3, 13, 27, -37], 1)
# This learned clause is a fact about the two adders alone: drop the
# miter's last clause ("some output differs") and the circuits can
# take any input, yet the negated clause still gives a contradiction.
circuits = cnf.clauses[:-1]
assert cnf.clauses[-1] == [39] and Cdcl(cnf.nvars, circuits).solve()
refute = Cdcl(cnf.nvars, circuits + [[-x] for x in s.shown[0]])
assert refute.solve() is False
print("   check: the two circuits alone, with the learned clause negated:"
      " UNSATISFIABLE")

print("2. the adder miter: decisions of dpll.py, conflicts of the others")
print("    N  variables  clauses      dpll   cdcl  cdcl_vsids")
want = {2: (12, 13), 3: (27, 35), 4: (54, 84), 5: (106, 116),
        6: (208, 229), 7: (410, 310), 8: (812, 673), 10: (3216, 585),
        12: (12820, 819), 16: (None, 1254), 32: (None, 2410)}
for n, expected in want.items():
    cnf = gen.adder_miter(n)
    row = f"   {n:2d}  {cnf.nvars:9d}  {len(cnf.clauses):7d}"
    if n <= 7:
        result, s = run(Dpll, cnf)
        assert result is False and s.decisions == 4 ** n - 1
        row += f"  {s.decisions:8,d}"
    else:
        row += "         -"
    got = []
    for solver, limit in ((Cdcl, 12), (CdclVsids, 32)):
        if n > limit:
            row += "       -"
            got.append(None)
            continue
        result, s = run(solver, cnf)
        assert result is False, "the two adders are equal"
        row += f"  {s.conflicts:6,d}" if solver is Cdcl \
            else f"  {s.conflicts:10,d}"
        got.append(s.conflicts)
    print(row)
    assert tuple(got) == expected, (n, got)
print("   UNSATISFIABLE in every cell; - means not run at that width")

print("3. the miter with one gate wrong (satisfiable)")
for n in (8, 12):
    cnf = gen.adder_miter(n, bug=True)
    r1, d = run(Dpll, cnf)
    r2, c = run(Cdcl, cnf)
    assert r1 is True and r2 is True
    print(f"   N = {n:2d}: dpll.py {d.decisions:,} decisions and "
          f"{d.conflicts:,} conflicts; cdcl.py {c.decisions} and "
          f"{c.conflicts}")
