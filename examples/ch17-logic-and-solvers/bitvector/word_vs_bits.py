"""word_vs_bits.py -- one question, asked of words and asked of bits.

    python3 word_vs_bits.py

"Is multiplication commutative at width w?", three ways, each as a
search for a counterexample that should not exist:

  rewrite   a*b != b*a on z3 bit-vectors.
  word      shift_add(a,b) != shift_add(b,a), where shift_add is the
            shift-and-add multiplier written with word-level
            operators, so the two sides are different terms.
  bits      the same multiplier as gates, turned into clauses by the
            chapter's own encoder (gen.py) and given to z3 as a
            purely Boolean problem.

Then four smaller facts about bit-vector arithmetic. Only verdicts
are printed: times belong to one machine and one solver version.
Needs the z3 Python package; prints "skipped" without it.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
try:
    import z3
except ImportError:
    print("skipped: the z3 Python package is not installed")
    sys.exit(0)
import gen  # noqa: E402


def shift_add(a, b, w):
    """Sum of the shifted copies of a selected by the bits of b."""
    acc = z3.BitVecVal(0, w)
    for i in range(w):
        row = z3.If(z3.Extract(i, i, b) == 1, a << i, z3.BitVecVal(0, w))
        acc = acc + row
    return acc


def ask(formula):
    s = z3.SolverFor("QF_BV")
    s.add(formula)
    return s, str(s.check())


def ask_bits(w):
    cnf = gen.multiplier_miter(w)
    x = [None] + [z3.Bool(f"x{v}") for v in range(1, cnf.nvars + 1)]
    s = z3.Solver()
    for c in cnf.clauses:
        s.add(z3.Or([x[v] if v > 0 else z3.Not(x[-v]) for v in c]))
    return str(s.check()), cnf


print("1. is there a, b with a*b != b*a?")
print("   width  rewrite  word   bits   (bits: variables, clauses)")
for w in range(4, 9):
    a, b = z3.BitVecs("a b", w)
    _, r0 = ask(a * b != b * a)
    _, r1 = ask(shift_add(a, b, w) != shift_add(b, a, w))
    r2, cnf = ask_bits(w)
    print(f"   {w:5d}  {r0:7s}  {r1:5s}  {r2:5s}  "
          f"({cnf.nvars}, {len(cnf.clauses)})")
    assert (r0, r1, r2) == ("unsat", "unsat", "unsat")
a, b = z3.BitVecs("a b", 64)
print("   width 64, rewrite:", ask(a * b != b * a)[1])
print("   simplify(a*b != b*a) =", z3.simplify(a * b != b * a))
assert z3.is_false(z3.simplify(a * b != b * a))

print("2. a false identity: is there a, b with a - b != b - a? (8 bits)")
a, b, x = z3.BitVecs("a b x", 8)
s, r = ask(a - b != b - a)
m = s.model()
va, vb = m[a].as_long(), m[b].as_long()
ok = (va - vb) % 256 != (vb - va) % 256
print(f"   {r}: a counterexample exists; checked by evaluating it: {ok}")
assert r == "sat" and ok

print("3. arithmetic is modulo 2^8: is there x with x + 255 != x - 1?")
print("   " + ask(x + 255 != x - 1)[1])
assert ask(x + 255 != x - 1)[1] == "unsat"

print("4. division by zero has a value: is there x with ...")
r1 = ask(z3.UDiv(x, 0) != 255)[1]
r2 = ask(z3.URem(x, 0) != x)[1]
print(f"   bvudiv(x, 0) != 255: {r1};  bvurem(x, 0) != x: {r2}")
assert (r1, r2) == ("unsat", "unsat")

print("5. '<' in z3's Python interface is signed: is there a, b where")
r1 = ask((a < b) != z3.ULT(a, b))[1]
r2 = ask(z3.And((a < b) != z3.ULT(a, b), z3.ULT(a, 128), z3.ULT(b, 128)))[1]
print(f"   (a < b) differs from ULT(a, b): {r1};  "
      f"with both below 128: {r2}")
assert (r1, r2) == ("sat", "unsat")
