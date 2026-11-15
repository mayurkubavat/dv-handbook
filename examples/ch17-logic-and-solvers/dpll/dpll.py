"""dpll.py -- the Davis-Putnam-Logemann-Loveland procedure, plainly.

    python3 dpll.py file.cnf [max_decisions]

Assign a variable, propagate every clause that has become a unit, and
on a conflict undo the most recent decision and try its other value.
Nothing is remembered about why a branch failed.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "common"))
import dimacs  # noqa: E402


class Dpll:
    def __init__(self, nvars, clauses, limit=None):
        self.nvars, self.clauses, self.limit = nvars, clauses, limit
        self.value = {}                 # variable -> True/False
        self.trail = []                 # literals in assignment order
        self.decisions = self.conflicts = self.propagations = 0
        self.log = None                 # a list here records the search

    def lit_value(self, lit):
        v = self.value.get(abs(lit))
        return None if v is None else v == (lit > 0)

    def assign(self, lit, why):
        self.value[abs(lit)] = lit > 0
        self.trail.append(lit)
        if self.log is not None:
            self.log.append((why, lit))

    def propagate(self):
        """Unit propagation to a fixed point; False on a conflict."""
        changed = True
        while changed:
            changed = False
            for clause in self.clauses:
                unassigned, satisfied = [], False
                for lit in clause:
                    v = self.lit_value(lit)
                    if v is True:
                        satisfied = True
                        break
                    if v is None:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:      # every literal is false
                    self.conflicts += 1
                    if self.log is not None:
                        self.log.append(("conflict", clause))
                    return False
                if len(unassigned) == 1:
                    self.assign(unassigned[0], clause)
                    self.propagations += 1
                    changed = True
        return True

    def undo_to(self, size):
        while len(self.trail) > size:
            del self.value[abs(self.trail.pop())]

    def solve(self):
        """True (satisfiable), False (not), None (limit reached)."""
        stack = []                      # (trail size, literal still to try)
        ok = self.propagate()
        while True:
            if ok:
                var = next((v for v in range(1, self.nvars + 1)
                            if v not in self.value), None)
                if var is None:
                    return True
                if self.limit and self.decisions >= self.limit:
                    return None
                self.decisions += 1
                stack.append((len(self.trail), -var))
                self.assign(var, "decide")      # try true first
            else:
                if not stack:
                    return False
                size, other = stack.pop()
                self.undo_to(size)
                self.assign(other, "flip")      # the other value, forced
            ok = self.propagate()

    def model(self):
        return [v if self.value.get(v) else -v
                for v in range(1, self.nvars + 1)]


def main(solver=Dpll):
    nvars, clauses = dimacs.read(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    s = solver(nvars, clauses, limit)
    result = s.solve()
    word = {True: "SATISFIABLE", False: "UNSATISFIABLE", None: "UNKNOWN"}
    print(f"s {word[result]}")
    print(f"c decisions {s.decisions} conflicts {s.conflicts} "
          f"propagations {s.propagations}")
    if result:
        print("v " + " ".join(map(str, s.model())) + " 0")


if __name__ == "__main__":
    main()
