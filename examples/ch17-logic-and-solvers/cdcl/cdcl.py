"""cdcl.py -- conflict-driven clause learning, in its smallest form.

    python3 cdcl.py file.cnf [max_conflicts]

The same search as dpll.py (first unassigned variable, true first),
with three additions: every assignment records the clause that forced
it, a conflict is analyzed back to the first unique implication point
and the result is kept as a new clause, and the search jumps back to
the level where that clause becomes a unit. Propagation looks only at
clauses that watch the literal that has just become false.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "common"))
import dimacs  # noqa: E402


class Cdcl:
    def __init__(self, nvars, clauses, limit=None):
        self.nvars, self.limit = nvars, limit
        self.clauses = []
        self.watches = {x: [] for v in range(1, nvars + 1) for x in (v, -v)}
        self.value, self.level, self.reason = {}, {}, {}
        self.trail, self.trail_lim, self.qhead = [], [], 0
        self.decisions = self.conflicts = self.propagations = 0
        self.learned, self.ok = 0, True
        for c in clauses:
            self.ok = self.ok and self.add_clause(sorted(set(c), key=abs))

    def lit_value(self, lit):
        v = self.value.get(abs(lit))
        return None if v is None else v == (lit > 0)

    def add_clause(self, c):
        """Attach a clause; False if it is empty or a falsified unit."""
        if any(-x in c for x in c):
            return True                 # contains x and not x: always true
        if len(c) == 1:
            if self.lit_value(c[0]) is False:
                return False
            if self.lit_value(c[0]) is None:
                self.assign(c[0], None)
            return True
        if not c:
            return False
        self.clauses.append(c)
        self.watches[c[0]].append(c)
        self.watches[c[1]].append(c)
        return True

    def assign(self, lit, reason):
        self.value[abs(lit)] = lit > 0
        self.level[abs(lit)] = len(self.trail_lim)
        self.reason[abs(lit)] = reason
        self.trail.append(lit)

    def propagate(self):
        """Return a falsified clause, or None when nothing is left."""
        while self.qhead < len(self.trail):
            false_lit = -self.trail[self.qhead]
            self.qhead += 1
            watching, self.watches[false_lit] = self.watches[false_lit], []
            for i, c in enumerate(watching):
                if c[0] == false_lit:   # keep the false watch in slot 1
                    c[0], c[1] = c[1], c[0]
                if self.lit_value(c[0]) is True:
                    self.watches[false_lit].append(c)
                    continue
                for k in range(2, len(c)):          # find a new watch
                    if self.lit_value(c[k]) is not False:
                        c[1], c[k] = c[k], c[1]
                        self.watches[c[1]].append(c)
                        break
                else:                   # none: c is a unit or a conflict
                    self.watches[false_lit].append(c)
                    if self.lit_value(c[0]) is False:
                        self.watches[false_lit] += watching[i + 1:]
                        return c
                    self.assign(c[0], c)
                    self.propagations += 1
        return None

    def analyze(self, conflict):
        """First-UIP learning: (learned clause, level to jump back to)."""
        here = len(self.trail_lim)
        seen, learned, open_paths = set(), [], 0
        clause, index, uip = conflict, len(self.trail) - 1, None
        while True:
            for lit in clause:
                var = abs(lit)
                if var in seen or self.level[var] == 0:
                    continue
                seen.add(var)
                if self.level[var] == here:
                    open_paths += 1     # still to be resolved away
                else:
                    learned.append(lit)
            while abs(self.trail[index]) not in seen:
                index -= 1
            uip = self.trail[index]
            index -= 1
            open_paths -= 1
            if open_paths == 0:
                break
            clause = self.reason[abs(uip)]
        learned.sort(key=lambda x: -self.level[abs(x)])
        back = self.level[abs(learned[0])] if learned else 0
        return [-uip] + learned, back

    def backjump(self, level):
        size = self.trail_lim[level]
        for lit in self.trail[size:]:
            del self.value[abs(lit)]
        del self.trail[size:], self.trail_lim[level:]
        self.qhead = size

    def pick(self):
        """The next variable to decide: the first one without a value."""
        return next((v for v in range(1, self.nvars + 1)
                     if v not in self.value), None)

    def solve(self):
        """True (satisfiable), False (not), None (limit reached)."""
        if not self.ok:
            return False
        while True:
            conflict = self.propagate()
            if conflict is not None:
                self.conflicts += 1
                if not self.trail_lim:
                    return False        # conflict with no decision to blame
                if self.limit and self.conflicts >= self.limit:
                    return None
                learned, back = self.analyze(conflict)
                self.backjump(back)
                self.learned += 1
                if len(learned) > 1:
                    self.clauses.append(learned)
                    self.watches[learned[0]].append(learned)
                    self.watches[learned[1]].append(learned)
                self.assign(learned[0], learned if len(learned) > 1 else None)
            else:
                var = self.pick()
                if var is None:
                    return True
                self.decisions += 1
                self.trail_lim.append(len(self.trail))
                self.assign(var, None)

    def model(self):
        return [v if self.value[v] else -v for v in range(1, self.nvars + 1)]


def main(solver=Cdcl):
    nvars, clauses = dimacs.read(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    s = solver(nvars, clauses, limit)
    result = s.solve()
    word = {True: "SATISFIABLE", False: "UNSATISFIABLE", None: "UNKNOWN"}
    print(f"s {word[result]}")
    print(f"c decisions {s.decisions} conflicts {s.conflicts} "
          f"propagations {s.propagations} learned {s.learned}")
    if result:
        print("v " + " ".join(map(str, s.model())) + " 0")


if __name__ == "__main__":
    main()
