"""cdcl_vsids.py -- cdcl.py with a decision heuristic.

    python3 cdcl_vsids.py file.cnf [max_conflicts]

The only change is which variable is decided next: each variable has
an activity that is raised when it appears in a learned clause, recent
conflicts count for more than old ones, and the search branches on the
most active unassigned variable instead of the lowest-numbered one.
This is an activity heuristic in the style of Chaff's VSIDS, not a
reimplementation of it.
"""
from cdcl import Cdcl, main


class CdclVsids(Cdcl):
    def __init__(self, nvars, clauses, limit=None):
        self.activity = {v: 0.0 for v in range(1, nvars + 1)}
        self.bump = 1.0
        super().__init__(nvars, clauses, limit)

    def analyze(self, conflict):
        learned, back = super().analyze(conflict)
        for lit in learned:
            self.activity[abs(lit)] += self.bump
        self.bump /= 0.95               # older conflicts fade
        if self.bump > 2.0 ** 512:      # rescale before a float overflows
            self.bump *= 2.0 ** -512
            for var in self.activity:
                self.activity[var] *= 2.0 ** -512
        return learned, back

    def pick(self):
        free = [v for v in range(1, self.nvars + 1) if v not in self.value]
        return max(free, key=self.activity.get) if free else None


if __name__ == "__main__":
    main(CdclVsids)
