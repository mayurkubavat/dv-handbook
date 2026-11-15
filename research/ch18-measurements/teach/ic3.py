"""ic3.py -- IC3 / PDR on an AIGER model, in its smallest honest form.

    python3 ic3.py model.aag

A cube is a tuple of (latch index, value) pairs: a set of states. A
lemma is the negation of a cube: "the design is never in these
states". frames[i] holds the lemmas known to hold for the first i
steps and not yet shown for i + 1; F_i, the states the engine still
thinks reachable within i steps, is every lemma in frames[i] and
later. The engine never unrolls: every question is about ONE step.
"""
import sys
from ts import Aig, Frame, solve, init_values, QUERIES


class Ic3:
    def __init__(self, aig, report=None):
        self.aig, self.report = aig, report or (lambda *_: None)
        self.f = Frame(aig)
        self.f.add()                        # the one copy of the logic
        self.step = self.f.clauses + self.f.constr(0)
        self.n = len(aig.latches)
        self.init = init_values(aig)
        self.frames = [[], []]              # frames[0] is unused
        self.lemmas = 0

    # -- the three questions -------------------------------------------
    def cube_lits(self, cube, nxt=False):
        pick = self.f.nxt if nxt else self.f.latch
        return [pick(0, i) if v else -pick(0, i) for i, v in cube]

    def frame(self, i):
        """Clauses of F_i over the current state."""
        if i == 0:
            return [[x] for x in self.cube_lits(sorted(self.init.items()))]
        return [[-x for x in self.cube_lits(c)]
                for level in self.frames[i:] for c in level]

    def state(self, model):
        return tuple((i, int(self.f.latch(0, i) in model))
                     for i in range(self.n))

    def bad_in(self, i):
        """A state of F_i that is bad, or None."""
        m = solve(self.f.nvars, self.step + self.frame(i)
                  + [[self.f.bad(0)]])
        return None if m is None else self.state(m)

    def pred(self, cube, i, exclude=True):
        """A state of F_i (outside the cube) with a step into the cube,
        or None: then the cube is unreachable in i + 1 steps."""
        q = self.step + self.frame(i)
        if exclude:
            q = q + [[-x for x in self.cube_lits(cube)]]
        q = q + [[x] for x in self.cube_lits(cube, nxt=True)]
        m = solve(self.f.nvars, q)
        return None if m is None else self.state(m)

    def meets_init(self, cube):
        return all(self.init.get(i, v) == v for i, v in cube)

    # -- blocking --------------------------------------------------------
    def generalize(self, cube, i):
        """Drop literals while the smaller cube still excludes every
        reset state and still has no predecessor in F_i."""
        for lit in cube:
            if len(cube) == 1:
                break
            smaller = tuple(x for x in cube if x != lit)
            if not self.meets_init(smaller) and \
                    self.pred(smaller, i) is None:
                cube = smaller
        return cube

    def block(self, cube, k):
        """Remove a bad state from F_k, or return a counterexample."""
        todo = [(k, cube, None)]            # proof obligations
        while todo:
            i, c, child = min(todo, key=lambda o: o[0])
            if i == 0:                      # a reset state: a real trace
                trace, o = [], (i, c, child)
                while o:
                    trace.append(o[1])
                    o = o[2]
                return trace
            assert not self.meets_init(c)   # or an earlier frame lied
            p = self.pred(c, i - 1)
            if p is not None:
                todo.append((i - 1, p, (i, c, child)))
                continue
            todo.remove((i, c, child))
            g = self.generalize(c, i - 1)
            for level in self.frames[1:i]:  # subsumed copies lower down
                if g in level:
                    level.remove(g)
            self.frames[i].append(g)
            self.lemmas += 1
            self.report(f"  lemma at frame {i}: never {show(g)}")
        return None

    def propagate(self, k):
        """Push lemmas forward; True when two frames have become equal."""
        for i in range(1, k + 1):
            for c in list(self.frames[i]):
                if self.pred(c, i, exclude=False) is None:
                    self.frames[i].remove(c)
                    self.frames[i + 1].append(c)
            if not self.frames[i]:
                self.fix = i
                return True
        return False

    def run(self):
        m = solve(self.f.nvars, self.step + self.frame(0)
                  + [[self.f.bad(0)]])
        if m is not None:
            return "cex", [self.state(m)]
        k = 1
        while True:
            while True:
                s = self.bad_in(k)
                if s is None:
                    break
                trace = self.block(s, k)
                if trace:
                    return "cex", trace
            self.frames.append([])
            self.report(f"frame {k}: no bad state left; sizes "
                        f"{[len(x) for x in self.frames[1:]]}")
            if self.propagate(k):
                inv = [c for level in self.frames[self.fix + 1:]
                       for c in level]
                return "proven", inv
            k += 1


def show(cube):
    return " ".join(f"l{i}={v}" for i, v in cube)


def certify(aig, inv):
    """The three checks of an inductive invariant, by fresh queries."""
    e = Ic3(aig)
    lemmas = [[-x for x in e.cube_lits(c)] for c in inv]
    a = all(not e.meets_init(c) for c in inv)           # reset is inside
    b = all(solve(e.f.nvars, e.step + lemmas
                  + [[x] for x in e.cube_lits(c, nxt=True)]) is None
            for c in inv)                               # a step stays in
    c = solve(e.f.nvars, e.step + lemmas + [[e.f.bad(0)]]) is None
    return a, b, c


if __name__ == "__main__":
    aig = Aig(sys.argv[1])
    verdict, what = Ic3(aig, print).run()
    if verdict == "proven":
        print(f"proven: invariant of {len(what)} lemmas; "
              f"checks {certify(aig, what)}")
    else:
        print(f"cex: depth {len(what) - 1}")
    print("queries", QUERIES[0])
