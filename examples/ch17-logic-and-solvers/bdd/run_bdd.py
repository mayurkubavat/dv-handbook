"""run_bdd.py -- canonicity, and what the variable order costs.

    python3 run_bdd.py

1. Two different carry circuits build the same node: equivalence
   without a search. A wrong gate builds another node, and the XOR of
   the two diagrams counts the inputs on which they differ.
2. The carry out of an N-bit adder under two variable orders.
3. Bit N-1 of an N-bit product under three orders.
Sizes are decision nodes; the two terminals are not counted.
"""
import sys

from robdd import AND, OR, XOR, Bdd

sys.setrecursionlimit(10000)


def names(n):
    return [f"a{i}" for i in range(n)], [f"b{i}" for i in range(n)]


def interleaved(n):
    a, b = names(n)
    return [v for pair in zip(a, b) for v in pair]


def separated(n):
    a, b = names(n)
    return a + b


def opposed(n):
    a, b = names(n)
    return [v for pair in zip(a, reversed(b)) for v in pair]


def add(d, xs, ys):
    """Ripple-carry addition of two lists of diagrams: (sums, carry)."""
    out, c = [], 0
    for x, y in zip(xs, ys):
        p = d.apply(XOR, x, y)
        out.append(d.apply(XOR, p, c))
        c = d.apply(OR, d.apply(AND, x, y), d.apply(AND, p, c))
    return out, c


def majority_carry(d, xs, ys, bug_at=None):
    """The carry out, each column's carry as a majority of three."""
    c = 0
    for i, (x, y) in enumerate(zip(xs, ys)):
        xy = d.apply(OR if i == bug_at else AND, x, y)
        c = d.apply(OR, xy, d.apply(OR, d.apply(AND, x, c),
                                    d.apply(AND, y, c)))
    return c


def carry_size(n, order):
    d = Bdd(order(n))
    a, b = names(n)
    return d.size(add(d, [d.var(v) for v in a], [d.var(v) for v in b])[1])


def product_bit_size(n, order):
    """Bit n-1 of a*b, by shift and add."""
    d = Bdd(order(n))
    a, b = names(n)
    acc = [0] * n
    for i in range(n):
        row = [0] * i + [d.apply(AND, d.var(a[j]), d.var(b[i]))
                         for j in range(n - i)]
        acc, _ = add(d, acc, row)
    return d.size(acc[n - 1])


print("1. equivalence by canonicity, 4-bit carry out, order a0 b0 a1 b1 ..")
d = Bdd(interleaved(4))
a, b = ([d.var(v) for v in vs] for vs in names(4))
ripple, maj = add(d, a, b)[1], majority_carry(d, a, b)
wrong = majority_carry(d, a, b, bug_at=3)
print(f"   ripple carry: node {ripple}; majority carry: node {maj}; "
      f"same node: {ripple == maj}")
differ = d.apply(XOR, ripple, wrong)
print(f"   one gate wrong: node {wrong}; same node: {ripple == wrong}; "
      f"they differ on {d.count(differ)} of {2 ** 8} inputs")
assert ripple == maj and ripple != wrong
brute = sum(((x + y) >> 4) != (((x + y) >> 4) | ((x ^ y) >> 3))
            for x in range(16) for y in range(16))
assert d.count(differ) == brute, "the count disagrees with enumeration"

print("2. decision nodes of an N-bit adder's carry out, by variable order")
print("    N  a0 b0 a1 b1 ..  3N - 1   a0 a1 .. b0 b1 ..  2^(N+1) - 2")
for n in range(1, 11):
    inter, sep = carry_size(n, interleaved), carry_size(n, separated)
    print(f"   {n:2d}  {inter:14d}  {3 * n - 1:6d}   {sep:17,d}  "
          f"{2 ** (n + 1) - 2:11,d}")
    assert inter == 3 * n - 1 and sep == 2 ** (n + 1) - 2

print("3. decision nodes of bit N-1 of an N-bit product, three orders")
print("    N  a0 b0 a1 b1 ..  a0 a1 .. b0 b1 ..  a0 b(N-1) a1 b(N-2) ..")
want = {2: 7, 3: 14, 4: 34, 5: 71, 6: 167, 7: 379, 8: 926, 9: 2186,
        10: 5246}
for n, expected in want.items():
    sizes = [product_bit_size(n, order)
             for order in (interleaved, separated, opposed)]
    print(f"   {n:2d}  {sizes[0]:14,d}  {sizes[1]:17,d}  {sizes[2]:22,d}")
    assert sizes[0] == expected, (n, sizes)
