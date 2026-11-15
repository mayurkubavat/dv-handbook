"""fuzz.py -- the chapter's engines against explicit-state search.

    python3 fuzz.py [cases] [seed]

Builds random small transition systems (2 to 6 latches, 1 to 3
inputs, sometimes an environment constraint) and every single-edge
mutant of the two-entry FIFO model, and runs three engines on each:
ic3.py, kind.py and kind.py with the simple-path constraint. The
referee is `explicit` in ts.py, which enumerates states and uses no
solver. Every verdict must agree with it; every counterexample must
replay step by step and be a shortest one; every invariant must
contain the reachable states, be closed under a step and exclude the
bad states, checked by enumeration and again by the three queries.
One disagreement and the run fails.
"""
import copy
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
for sub in ("common", "ic3", "kind"):
    sys.path.insert(0, str(HERE.parent / sub))
from ts import Aig, evaluate, explicit, initial  # noqa: E402
from ic3 import Ic3, certify  # noqa: E402
from kind import kind  # noqa: E402

PLAIN_K, SIMPLE_K = 12, 20              # how far each induction goes


class Build:
    """A netlist builder: ANDs, with OR, XOR and MUX made from them."""

    def __init__(self, ni, nl):
        self.inputs = [2 * (i + 1) for i in range(ni)]
        self.lat = [2 * (ni + i + 1) for i in range(nl)]
        self.ands, self.top = [], ni + nl

    def AND(self, x, y):
        self.top += 1
        self.ands.append([2 * self.top, x, y])
        return 2 * self.top

    def OR(self, x, y):
        return self.AND(x ^ 1, y ^ 1) ^ 1

    def XOR(self, x, y):
        return self.OR(self.AND(x, y ^ 1), self.AND(x ^ 1, y))

    def MUX(self, s, x, y):
        return self.OR(self.AND(s, x), self.AND(s ^ 1, y))


def random_aig(rng):
    """Random logic, biased toward state that takes steps to reach:
    latches count, shift, hold or take a random literal; the bad
    state is a conjunction; three in ten have a constraint."""
    ni, nl = rng.randint(1, 3), rng.randint(2, 6)
    b = Build(ni, nl)
    pool = b.inputs + b.lat

    def anylit():
        return rng.choice(pool) ^ rng.randint(0, 1)

    for _ in range(rng.randint(0, 12)):
        op = rng.choice([b.AND, b.OR, b.XOR])
        pool.append(op(anylit(), anylit()))
    nxt, carry = [], rng.choice(b.inputs)
    style = rng.choice(["count", "shift", "mixed", "random"])
    for i, lat in enumerate(b.lat):
        how = style if style != "mixed" else \
            rng.choice(["count", "shift", "random", "hold"])
        if how == "count":                  # a counter bit with enable
            nxt.append(b.XOR(lat, carry))
            carry = b.AND(carry, lat)
        elif how == "shift":
            src = b.lat[i - 1] if i else anylit()
            nxt.append(b.MUX(rng.choice(b.inputs), src, lat))
        elif how == "hold":
            nxt.append(b.MUX(anylit(), anylit(), lat))
        else:
            nxt.append(anylit())
    a = object.__new__(Aig)                 # an Aig without a file
    a.inputs = b.inputs
    a.latches = [[lat, n, rng.choice([0, 0, 0, 1, lat])]
                 for lat, n in zip(b.lat, nxt)]
    bad = rng.choice(b.lat) ^ rng.randint(0, 1)
    for _ in range(rng.randint(0, min(nl, 5) - 1)):
        bad = b.AND(bad, rng.choice(b.lat + pool) ^ rng.randint(0, 1))
    a.bads = [bad]
    a.constraints = [b.OR(anylit(), anylit())] \
        if rng.random() < 0.3 else []
    a.ands, a.outputs, a.names, a.maxvar = b.ands, [], {}, b.top
    return a


def mutants(path):
    """The model with one inversion flipped: on one input of one AND,
    on one latch's next-state literal, or on the bad literal."""
    base = Aig(path)
    for i in range(len(base.ands)):
        for j in (1, 2):
            m = copy.deepcopy(base)
            m.ands[i][j] ^= 1
            yield m
    for i in range(len(base.latches)):
        m = copy.deepcopy(base)
        m.latches[i][1] ^= 1
        yield m
    m = copy.deepcopy(base)
    m.bads[0] ^= 1
    yield m


def replays(aig, states):
    """Is this list of integer states a run from reset to bad?"""
    every = range(1 << len(aig.inputs))
    if states[0] not in initial(aig):
        return False
    for s, t in zip(states, states[1:]):
        if not any(evaluate(aig, s, x)[:2] == (t, True) for x in every):
            return False
    return any(evaluate(aig, states[-1], x)[1:] == (True, True)
               for x in every)


def invariant_ok(aig, inv, reach):
    """By enumeration: every reachable state is inside, no step
    leaves, and no state inside is bad."""
    def inside(s):
        return not any(all((s >> i) & 1 == v for i, v in c) for c in inv)
    if not all(inside(s) for s in reach):
        return False
    for s in range(1 << len(aig.latches)):
        if not inside(s):
            continue
        for x in range(1 << len(aig.inputs)):
            nxt, ok, bad = evaluate(aig, s, x)
            if ok and (bad or not inside(nxt)):
                return False
    return True


def pack(bits):
    return sum(b << i for i, b in enumerate(bits))


class Tally:
    def __init__(self):
        self.n = self.proven = self.cex = self.wrong = 0
        self.deepest = self.largest = 0
        self.plain = {"proven": 0, "cex": 0, "undetermined": 0}
        self.simple = {"proven": 0, "cex": 0, "undetermined": 0}

    def case(self, aig, label):
        reach, depth = explicit(aig)
        want = "proven" if depth is None else "cex"
        self.n += 1
        self.proven += want == "proven"
        self.cex += want == "cex"
        self.deepest = max(self.deepest, depth or 0)
        bad = []
        verdict, what = Ic3(aig).run()
        if verdict != want:
            bad.append(f"ic3 says {verdict}")
        elif verdict == "cex":
            states = [pack(v for _, v in c) for c in what]
            if not replays(aig, states) or len(states) - 1 != depth:
                bad.append("ic3 counterexample")
        else:
            self.largest = max(self.largest, len(what))
            if not invariant_ok(aig, what, reach) \
                    or not all(certify(aig, what)):
                bad.append("ic3 invariant")
        for simple, limit, count in ((False, PLAIN_K, self.plain),
                                     (True, SIMPLE_K, self.simple)):
            verdict, k, path = kind(aig, limit, simple)
            count[verdict] += 1
            name = "simple-path induction" if simple else "induction"
            if verdict == "undetermined":
                # allowed: a true property that induction does not
                # reach, or a bug deeper than the limit
                if want == "cex" and depth <= limit:
                    bad.append(f"{name} missed a bug at {depth}")
            elif verdict != want:
                bad.append(f"{name} says {verdict}")
            elif verdict == "cex" and (
                    k != depth or not replays(aig, [pack(s) for s in path])):
                bad.append(f"{name} counterexample")
        for b in bad:
            print(f"WRONG: {label}: {b}; the referee says {want}"
                  + (f" at step {depth}" if depth is not None else ""))
        self.wrong += len(bad)

    def report(self, title):
        print(f"{title}: {self.n} systems; the referee finds "
              f"{self.proven} safe and {self.cex} unsafe")
        print(f"  deepest counterexample {self.deepest} steps; "
              f"largest invariant {self.largest} lemmas")
        for name, c in (("induction", self.plain),
                        ("simple-path induction", self.simple)):
            print(f"  {name}: {c['proven']} proven, {c['cex']} "
                  f"counterexamples, {c['undetermined']} undetermined")
        print(f"  wrong verdicts, traces or invariants: {self.wrong}")
        return self.wrong


if __name__ == "__main__":
    cases = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 18
    rng = random.Random(seed)
    t = Tally()
    for n in range(cases):
        t.case(random_aig(rng), f"seed {seed} case {n}")
    wrong = t.report(f"random systems, seed {seed}")
    t = Tally()
    for n, m in enumerate(mutants(HERE.parent / "common"
                                  / "fifo_ptrs2.aag")):
        t.case(m, f"mutant {n}")
    wrong += t.report("single-edge mutants of fifo_ptrs2.aag")
    if wrong:
        print(f"FAILED: {wrong} disagreements with the referee")
        sys.exit(1)
    print("self-test passed: no disagreement with explicit-state search")
