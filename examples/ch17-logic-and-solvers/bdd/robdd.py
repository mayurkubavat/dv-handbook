"""robdd.py -- reduced ordered binary decision diagrams in one page.

A node is an integer. 0 and 1 are the terminals; every other node is a
triple (level, low, high) kept in a unique table, so two nodes with
the same triple are the same integer, and a node whose two children
are equal is never created. Those two rules are the reduction, and
they make the diagram canonical: under one variable order, two
functions are equal exactly when their nodes are the same integer.
"""


class Bdd:
    def __init__(self, order):
        self.order = list(order)
        self.level = {name: i for i, name in enumerate(order)}
        self.nodes = [None, None]       # index -> (level, low, high)
        self.unique = {}                # (level, low, high) -> index
        self.memo = {}                  # (op, f, g) -> result

    def mk(self, level, low, high):
        if low == high:                 # the test does not matter
            return low
        key = (level, low, high)
        if key not in self.unique:      # share equal subgraphs
            self.unique[key] = len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def var(self, name):
        return self.mk(self.level[name], 0, 1)

    def top(self, f):
        return self.nodes[f][0] if f > 1 else len(self.level)

    def apply(self, op, f, g):
        """Combine two diagrams with a two-input Boolean operator."""
        if f <= 1 and g <= 1:
            return int(op(bool(f), bool(g)))
        key = (op, f, g)
        if key not in self.memo:
            level = min(self.top(f), self.top(g))
            f0, f1 = self.nodes[f][1:] if self.top(f) == level else (f, f)
            g0, g1 = self.nodes[g][1:] if self.top(g) == level else (g, g)
            self.memo[key] = self.mk(level, self.apply(op, f0, g0),
                                     self.apply(op, f1, g1))
        return self.memo[key]

    def reachable(self, f):
        """The decision nodes of f, as a set of integers."""
        seen, stack = set(), [f]
        while stack:
            n = stack.pop()
            if n > 1 and n not in seen:
                seen.add(n)
                stack += self.nodes[n][1:]
        return seen

    def size(self, f):
        return len(self.reachable(f))

    def count(self, f, level=0):
        """How many assignments of the variables make f true."""
        if f <= 1:
            return f << (len(self.level) - level)
        at, low, high = self.nodes[f]
        return (self.count(low, at + 1)
                + self.count(high, at + 1)) << (at - level)


def AND(x, y):
    return x and y


def OR(x, y):
    return x or y


def XOR(x, y):
    return x != y
