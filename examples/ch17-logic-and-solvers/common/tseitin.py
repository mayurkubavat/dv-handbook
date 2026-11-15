"""tseitin.py -- build CNF gate by gate (the Tseitin encoding).

Every gate output gets a fresh variable g and the clauses that say
"g equals the gate's function of its inputs". Literals are DIMACS
integers: variable v is v, its complement is -v, so an inverter costs
nothing: negate the literal.
"""


class Cnf:
    def __init__(self):
        self.nvars = 0
        self.clauses = []
        self.defs = {}                  # gate output -> (name, inputs)

    def var(self):
        self.nvars += 1
        return self.nvars

    def vars(self, n):
        return [self.var() for _ in range(n)]

    def add(self, *clause):
        self.clauses.append(list(clause))

    def and_(self, a, b):
        g = self.var()
        self.add(-g, a)                 # g -> a
        self.add(-g, b)                 # g -> b
        self.add(g, -a, -b)             # a and b -> g
        self.defs[g] = ("and", a, b)
        return g

    def or_(self, a, b):
        g = self.var()
        self.add(g, -a)                 # a -> g
        self.add(g, -b)                 # b -> g
        self.add(-g, a, b)              # g -> a or b
        self.defs[g] = ("or", a, b)
        return g

    def xor_(self, a, b):
        g = self.var()
        self.add(-g, a, b)              # g -> the inputs differ
        self.add(-g, -a, -b)
        self.add(g, -a, b)              # the inputs differ -> g
        self.add(g, a, -b)
        self.defs[g] = ("xor", a, b)
        return g

    def or_all(self, lits):
        g = self.var()
        self.add(-g, *lits)             # g -> some input
        for lit in lits:
            self.add(g, -lit)           # any input -> g
        self.defs[g] = ("or", *lits)
        return g
