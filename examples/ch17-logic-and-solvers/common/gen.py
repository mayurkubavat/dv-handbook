"""gen.py -- the instance families the chapter measures.

    python3 gen.py adder N out.cnf      two N-bit adders differ? (unsat)
    python3 gen.py adderbug N out.cnf   the same, one gate wrong (sat)
    python3 gen.py mul N out.cnf        N-bit a*b differs from b*a? (unsat)
    python3 gen.py php N out.cnf        N+1 pigeons in N holes (unsat)
    python3 gen.py rand N M SEED out.cnf   random 3-SAT, N vars, M clauses

In the two-operand families the operand bits are variables 1 to 2N,
a first and then b, least significant bit first.
"""
import random
import sys

import dimacs
from tseitin import Cnf


def full_adder(cnf, a, b, cin):
    """One column, as five gates; returns (sum, carry out)."""
    p = cnf.xor_(a, b)
    s = cnf.xor_(p, cin)
    g = cnf.and_(a, b)
    t = cnf.and_(p, cin)
    return s, cnf.or_(g, t)


def ripple(cnf, a, b):
    """Ripple-carry adder: the sum bits, then the carry out."""
    out, c = [], None
    for ai, bi in zip(a, b):
        if c is None:                   # a half adder in column 0
            out.append(cnf.xor_(ai, bi))
            c = cnf.and_(ai, bi)
        else:
            s, c = full_adder(cnf, ai, bi, c)
            out.append(s)
    return out + [c]


def majority(cnf, a, b, bug_at=None):
    """The same function, the carry written as a majority of three."""
    out, c = [], None
    for i, (ai, bi) in enumerate(zip(a, b)):
        if c is None:
            out.append(cnf.xor_(ai, bi))
            c = cnf.and_(ai, bi)
        else:
            out.append(cnf.xor_(ai, cnf.xor_(bi, c)))
            ab = cnf.or_(ai, bi) if i == bug_at else cnf.and_(ai, bi)
            c = cnf.or_(ab, cnf.or_(cnf.and_(ai, c), cnf.and_(bi, c)))
    return out + [c]


def adder_miter(n, bug=False):
    """Satisfiable exactly when the two adders differ on some input."""
    cnf = Cnf()
    a, b = cnf.vars(n), cnf.vars(n)
    s1 = ripple(cnf, a, b)
    s2 = majority(cnf, a, b, bug_at=n - 1 if bug else None)
    diff = [cnf.xor_(u, v) for u, v in zip(s1, s2)]
    cnf.add(cnf.or_all(diff))           # some output bit differs
    return cnf


def multiply(cnf, a, b):
    """Shift-and-add multiplier, low len(a) bits: add a<<i where b[i]."""
    n = len(a)
    acc = [cnf.and_(a[j], b[0]) for j in range(n)]
    for i in range(1, n):
        row = [cnf.and_(a[j], b[i]) for j in range(n - i)]
        acc[i:] = ripple(cnf, acc[i:], row)[:-1]    # drop the carry out
    return acc


def multiplier_miter(n):
    cnf = Cnf()
    a, b = cnf.vars(n), cnf.vars(n)
    p1, p2 = multiply(cnf, a, b), multiply(cnf, b, a)
    cnf.add(cnf.or_all([cnf.xor_(u, v) for u, v in zip(p1, p2)]))
    return cnf


def pigeonhole(n):
    cnf = Cnf()
    x = [cnf.vars(n) for _ in range(n + 1)]     # x[p][h]: p sits in h
    for p in range(n + 1):
        cnf.add(*x[p])                          # every pigeon sits
    for h in range(n):
        for p in range(n + 1):
            for q in range(p + 1, n + 1):
                cnf.add(-x[p][h], -x[q][h])     # no two share a hole
    return cnf


def random_3sat(n, m, seed):
    """m clauses, each over three distinct variables, signs by coin.

    Only Random.random() is used: it is the one method whose sequence
    Python's documentation promises to keep from version to version.
    """
    rng = random.Random(seed)
    cnf = Cnf()
    cnf.vars(n)
    for _ in range(m):
        vs = []
        while len(vs) < 3:
            v = 1 + int(rng.random() * n)
            if v not in vs:
                vs.append(v)
        cnf.add(*[v if rng.random() < 0.5 else -v for v in vs])
    return cnf


def main():
    kind, args, out = sys.argv[1], sys.argv[2:-1], sys.argv[-1]
    n = int(args[0])
    if kind == "rand":
        cnf = random_3sat(n, int(args[1]), int(args[2]))
    else:
        cnf = {"php": pigeonhole, "adder": adder_miter,
               "mul": multiplier_miter,
               "adderbug": lambda k: adder_miter(k, bug=True)}[kind](n)
    dimacs.write(out, cnf.nvars, cnf.clauses, " ".join(sys.argv[1:-1]))


if __name__ == "__main__":
    main()
