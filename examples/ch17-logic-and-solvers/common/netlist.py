"""netlist.py -- read a netlist of two-input gates from SystemVerilog.

Understands exactly one form, the one the chapter's full adder uses:

    input  logic a, b, cin,
    assign p = a ^ b;

and returns the inputs and the gates in file order.
"""
import re

GATE = re.compile(r"assign\s+(\w+)\s*=\s*(\w+)\s*([&|^])\s*(\w+)\s*;")
OPS = {"&": lambda x, y: x & y, "|": lambda x, y: x | y,
       "^": lambda x, y: x ^ y}


def read(path):
    """Return (input names, [(output, operator, left, right), ...])."""
    text = open(path).read()
    inputs = re.search(r"input\s+logic\s+([\w\s,]+?),\s*\n", text).group(1)
    inputs = [name.strip() for name in inputs.split(",")]
    return inputs, [(out, op, x, y)
                    for out, x, op, y in GATE.findall(text)]


def evaluate(inputs, gates, values):
    """Every signal's value for one tuple of input values."""
    sig = dict(zip(inputs, values))
    for out, op, x, y in gates:
        sig[out] = OPS[op](sig[x], sig[y])
    return sig
