"""fuzz.py -- the teaching engines against explicit-state search on
random small transition systems.

    python3 fuzz.py N [seed]
"""
import random
import sys
import collections
from ts import Aig, evaluate, explicit, init_values
import ic3 as ic3mod
import kind as kindmod


class Build:
    """A small netlist builder: ANDs with folding, XOR and MUX on top."""

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
    latches often hold, shift or count, and bad is a conjunction."""
    ni, nl = rng.randint(1, 3), rng.randint(2, 8)
    b = Build(ni, nl)
    pool = b.inputs + b.lat

    def anylit():
        return rng.choice(pool) ^ rng.randint(0, 1)

    for _ in range(rng.randint(0, 12)):
        op = rng.choice([b.AND, b.OR, b.XOR])
        pool.append(op(anylit(), anylit()))
    nxt, carry = [], rng.choice(b.inputs)
    style = rng.choice(["count", "shift", "mixed", "random"])
    for i, l in enumerate(b.lat):
        kind = style if style != "mixed" else \
            rng.choice(["count", "shift", "random", "hold"])
        if kind == "count":                 # a counter bit with enable
            nxt.append(b.XOR(l, carry))
            carry = b.AND(carry, l)
        elif kind == "shift":
            src = b.lat[i - 1] if i else anylit()
            nxt.append(b.MUX(rng.choice(b.inputs), src, l))
        elif kind == "hold":
            nxt.append(b.MUX(anylit(), anylit(), l))
        else:
            nxt.append(anylit())
    a = object.__new__(Aig)
    a.inputs, a.ands = b.inputs, b.ands
    a.latches = [[l, n, rng.choice([0, 0, 0, 1, l])]
                 for l, n in zip(b.lat, nxt)]
    bad = rng.choice(b.lat) ^ rng.randint(0, 1)
    for _ in range(rng.randint(0, min(nl, 5) - 1)):
        bad = b.AND(bad, rng.choice(b.lat + pool) ^ rng.randint(0, 1))
    a.ands = b.ands
    a.bads = [bad]
    a.constraints = [b.OR(anylit(), anylit())] \
        if rng.random() < 0.3 else []
    a.outputs, a.names, a.maxvar = [], {}, b.top
    return a


def check_trace(aig, trace):
    """Is this list of full-state cubes a real run from reset to bad?"""
    states = [sum(v << i for i, v in c) for c in trace]
    iv = init_values(aig)
    if any((states[0] >> i) & 1 != r for i, r in iv.items()):
        return False
    m = len(aig.inputs)
    for s, t in zip(states, states[1:]):
        if not any(evaluate(aig, s, x)[:2] == (t, True)
                   for x in range(1 << m)):
            return False
    return any(evaluate(aig, states[-1], x)[1:] == (True, True)
               for x in range(1 << m))


def check_inv(aig, inv, reach):
    """Explicitly: every reachable state satisfies every lemma, the
    lemma set is closed under a step, and no state in it is bad."""
    n, m = len(aig.latches), len(aig.inputs)
    def inside(s):
        return not any(all((s >> i) & 1 == v for i, v in c) for c in inv)
    if not all(inside(s) for s in reach):
        return False
    for s in range(1 << n):
        if not inside(s):
            continue
        for x in range(1 << m):
            nxt, ok, bad = evaluate(aig, s, x)
            if ok and (bad or not inside(nxt)):
                return False
    return True


def main(count, seed, engines="ic3,kind"):
    rng = random.Random(seed)
    tally = collections.Counter()
    for case in range(count):
        aig = random_aig(rng)
        if len(aig.latches) > 6 and "kind" in engines:
            continue
        reach, depth = explicit(aig)
        want = "proven" if depth is None else "cex"
        # IC3
        e = ic3mod.Ic3(aig)
        verdict, what = e.run()
        tally["ic3 frames max"] = max(tally["ic3 frames max"],
                                      len(e.frames) - 1)
        tally["ic3 lemmas total"] += e.lemmas
        ok = verdict == want
        if ok and verdict == "cex":
            ok = check_trace(aig, what) and len(what) - 1 >= depth
            tally["ic3 cex shortest"] += len(what) - 1 == depth
        if ok and verdict == "proven":
            ok = check_inv(aig, what, reach) and \
                all(ic3mod.certify(aig, what))
        tally[f"ic3 {verdict}"] += 1
        if not ok:
            print("IC3 MISMATCH", seed, case, verdict, want, depth)
            tally["ic3 WRONG"] += 1
        # k-induction, plain and with simple-path constraints
        for simple in ((False, True) if "kind" in engines else ()):
            name = "kind-sp" if simple else "kind"
            limit = 20 if simple else 12
            v, k, _ = kindmod.kind_aig(aig, limit, simple)
            tally[f"{name} {v}"] += 1
            good = (v == want and (v != "cex" or k == depth)) or \
                (v == "undetermined" and want == "proven")
            if v == "undetermined" and want == "cex" and depth > limit:
                good = True
            if not good:
                print("KIND MISMATCH", seed, case, name, v, k, want, depth)
                tally[f"{name} WRONG"] += 1
        tally["latches %d" % len(aig.latches)] += 1
        tally["reach depth max"] = max(tally["reach depth max"],
                                       depth or 0)
        tally["cex depth >= 3"] += (depth or 0) >= 3
        tally["cex depth >= 8"] += (depth or 0) >= 8
        if verdict == "proven":
            tally["inv lemmas max"] = max(tally["inv lemmas max"],
                                          len(what))
            tally["inv nonempty"] += len(what) > 0
            tally["inv >= 5 lemmas"] += len(what) >= 5
    for key in sorted(tally):
        print(f"{key:24s} {tally[key]}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 1,
         sys.argv[3] if len(sys.argv) > 3 else "ic3,kind")
