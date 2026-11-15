"""ic3.py -- IC3, also called PDR, on an AIGER model, kept small.

    python3 ic3.py model.aag

A cube is a tuple of (latch index, value) pairs and stands for the
set of states that agree with it. A lemma is a cube negated: "the
design is never in these states". frames[i] holds the cubes whose
lemmas are known to hold for the first i steps and are not yet shown
for i + 1. The frame F_i, the states the engine still believes
reachable within i steps, is every lemma in frames[i] and later; F_0
is the reset states. The engine never unrolls: each question is
about ONE copy of the logic.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "common"))
from ts import Aig, Frame, solve, init_values, QUERIES  # noqa: E402


class Ic3:
    def __init__(self, aig, report=lambda *_: None):
        self.aig, self.report = aig, report
        self.f = Frame(aig)
        self.f.add()                        # the one copy of the logic
        self.step = self.f.clauses + self.f.constr(0)
        self.n = len(aig.latches)
        self.init = init_values(aig)
        self.frames = [[], []]              # frames[0] is not used

    # -- the three questions ------------------------------------------
    def lits(self, cube, nxt=False):
        """A cube as literals, over this state or over the next."""
        pick = self.f.nxt if nxt else self.f.latch
        return [pick(0, i) if v else -pick(0, i) for i, v in cube]

    def frame(self, i):
        """The clauses of F_i, over the current state."""
        if i == 0:
            return [[x] for x in self.lits(sorted(self.init.items()))]
        return [[-x for x in self.lits(c)]
                for level in self.frames[i:] for c in level]

    def state(self, model):
        return tuple((i, int(self.f.latch(0, i) in model))
                     for i in range(self.n))

    def bad_in(self, i):
        """Question 1: a bad state of F_i, or None."""
        m = solve(self.f.nvars, self.step + self.frame(i)
                  + [[self.f.bad(0)]])
        return None if m is None else self.state(m)

    def pred(self, cube, i):
        """Question 2: a state of F_i outside the cube with a step
        into the cube, or None. None says the lemma of this cube is
        inductive relative to F_i."""
        m = solve(self.f.nvars, self.step + self.frame(i)
                  + [[-x for x in self.lits(cube)]]
                  + [[x] for x in self.lits(cube, nxt=True)])
        return None if m is None else self.state(m)

    def holds_next(self, cube, i):
        """Question 3: does every step out of F_i avoid the cube?"""
        return solve(self.f.nvars, self.step + self.frame(i)
                     + [[x] for x in self.lits(cube, nxt=True)]) is None

    def meets_init(self, cube):
        """Does the cube contain a reset state?"""
        return all(self.init.get(i, v) == v for i, v in cube)

    # -- blocking -----------------------------------------------------
    def generalize(self, cube, i):
        """Drop literals one at a time while the smaller cube still
        holds no reset state and still has no predecessor in F_i."""
        for lit in cube:
            smaller = tuple(x for x in cube if x != lit)
            if smaller and not self.meets_init(smaller) \
                    and self.pred(smaller, i) is None:
                cube = smaller
        return cube

    def block(self, cube, k):
        """Remove a bad state from F_k. Returns a counterexample, a
        list of states from reset to the bad one, or None."""
        todo = [(k, cube, None)]            # proof obligations
        while todo:
            i, c, child = min(todo, key=lambda o: o[0])
            if i == 0:                      # a reset state: a real path
                trace, o = [], (i, c, child)
                while o:
                    trace.append(o[1])
                    o = o[2]
                return trace
            assert not self.meets_init(c)   # or an earlier frame lied
            p = self.pred(c, i - 1)
            if p is not None:               # first deal with p
                self.report("obligation", i - 1, p, c)
                todo.append((i - 1, p, (i, c, child)))
                continue
            todo.remove((i, c, child))
            g = self.generalize(c, i - 1)
            for level in self.frames[1:i]:  # the same cube, lower down
                if g in level:
                    level.remove(g)
            self.frames[i].append(g)
            self.report("lemma", i, c, g)
        return None

    # -- propagation and the main loop --------------------------------
    def propagate(self, k):
        """Move each lemma up as far as it holds. True when a frame
        has handed on every lemma, so that F_i equals F_i+1."""
        for i in range(1, k + 1):
            for c in list(self.frames[i]):
                if self.holds_next(c, i):
                    self.frames[i].remove(c)
                    self.frames[i + 1].append(c)
            if not self.frames[i]:
                self.fix = i
                return True
        return False

    def run(self):
        """("cex", states) or ("proven", cubes of the invariant)."""
        m = solve(self.f.nvars, self.step + self.frame(0)
                  + [[self.f.bad(0)]])
        if m is not None:                   # a reset state is bad
            return "cex", [self.state(m)]
        k = 1
        while True:
            while True:
                s = self.bad_in(k)
                if s is None:
                    break
                self.report("bad", k, s)
                trace = self.block(s, k)
                if trace:
                    return "cex", trace
            self.frames.append([])
            self.report("frontier", k)
            if self.propagate(k):
                self.report("fixed", self.fix)
                return "proven", [c for level in self.frames[self.fix + 1:]
                                  for c in level]
            self.report("pushed", k)
            k += 1


def certify(aig, inv):
    """The three checks of an inductive invariant, by fresh queries:
    it holds in reset, a step cannot leave it, no state in it is bad."""
    e = Ic3(aig)
    lemmas = [[-x for x in e.lits(c)] for c in inv]
    start = all(not e.meets_init(c) for c in inv)
    closed = all(solve(e.f.nvars, e.step + lemmas
                       + [[x] for x in e.lits(c, nxt=True)]) is None
                 for c in inv)
    safe = solve(e.f.nvars, e.step + lemmas + [[e.f.bad(0)]]) is None
    return start, closed, safe


if __name__ == "__main__":
    model = Aig(sys.argv[1])
    verdict, what = Ic3(model).run()
    if verdict == "proven":
        print(f"proven: an invariant of {len(what)} lemmas; "
              f"checks {certify(model, what)}")
    else:
        print(f"cex: {len(what) - 1} steps")
    print("queries", QUERIES[0])
