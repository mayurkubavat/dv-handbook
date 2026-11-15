"""aiger.py -- read an and-inverter graph in the ASCII AIGER format.

The header is "aag M I L O A" and, from AIGER 1.9, optionally "B C":
the largest variable index, then the numbers of inputs, latches,
outputs, AND gates, bad-state literals and constraint literals. The
body lists them in that order, except that the ANDs come last. A
literal is twice a variable index, plus one if it is inverted; 0 and
1 are the constants false and true.
"""


class Aig:
    def __init__(self, path):
        with open(path) as f:
            rows = [line.split() for line in f]
        assert rows[0][0] == "aag", "not an ASCII AIGER file"
        head = [int(x) for x in rows[0][1:]] + [0, 0]
        self.maxvar, i, n, o, a, b, c = head[:7]
        body = [[int(x) for x in r] for r in rows[1:1 + i + n + o + b + c + a]]
        self.inputs = [r[0] for r in body[:i]]
        self.latches = body[i:i + n]    # literal, next, [reset value]
        body = body[i + n:]
        self.outputs = [r[0] for r in body[:o]]
        self.bads = [r[0] for r in body[o:o + b]]
        self.constraints = [r[0] for r in body[o + b:o + b + c]]
        self.ands = body[o + b + c:]    # output, left input, right input
        self.names = {}                 # e.g. "i0" -> "a", from the symbols
        for r in rows[1 + len(body) + i + n:]:
            if r and r[0] == "c":
                break
            if len(r) == 2:
                self.names[r[0]] = r[1]


def show(lit):
    """A literal as text: v4 is variable 4, !v4 its complement."""
    if lit < 2:
        return str(lit)
    return ("!" if lit & 1 else "") + f"v{lit >> 1}"
