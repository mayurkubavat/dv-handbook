"""encode.py -- the full adder as clauses, by hand and by program.

    python3 encode.py

Reads the hand-written full_adder.cnf, builds the same circuit with
the gate-by-gate builder from the SystemVerilog source, and compares
the two. Then it checks what the encoding claims, by trying all 256
assignments of the eight variables: the clauses hold exactly on the
eight rows of the truth table. Then it asks two questions by adding
unit clauses and counting the assignments that survive, and last it
shows what one missing clause does to the first answer.
"""
import itertools
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
import dimacs  # noqa: E402
import netlist  # noqa: E402
from tseitin import Cnf  # noqa: E402

nvars, hand = dimacs.read(HERE / "full_adder.cnf")
print(f"hand encoding:    {nvars} variables, {len(hand)} clauses")

inputs, gates = netlist.read(HERE.parent / "truth-table" / "full_adder.sv")
cnf = Cnf()
var = {name: cnf.var() for name in inputs}
build = {"&": cnf.and_, "|": cnf.or_, "^": cnf.xor_}
for out, op, x, y in gates:
    var[out] = build[op](var[x], var[y])
print(f"builder encoding: {cnf.nvars} variables, {len(cnf.clauses)} "
      f"clauses, {len(gates)} gates")
print("numbering: " + " ".join(f"{v}={name}" for name, v in var.items()))


def as_set(clauses):
    return {frozenset(c) for c in clauses}


same = as_set(hand) == as_set(cnf.clauses)
print("the two encodings are the same set of clauses:", same)
assert same and nvars == cnf.nvars == 8 and len(hand) == 17


def models(clauses):
    """Every assignment of the variables that satisfies every clause."""
    found = []
    for bits in itertools.product((0, 1), repeat=nvars):
        if all(any(bits[abs(x) - 1] == (x > 0) for x in c) for c in clauses):
            found.append(bits)
    return found


rows = models(hand)
circuit = [tuple(netlist.evaluate(inputs, gates, r)[n] for n in var)
           for r in itertools.product((0, 1), repeat=len(inputs))]
print(f"{2 ** nvars} assignments tried; {len(rows)} satisfy the clauses; "
      f"they are the truth table: {sorted(rows) == sorted(circuit)}")
assert sorted(rows) == sorted(circuit)

for text, units in (("sum=1 cout=1 a=0", [5, 8, -1]),
                    ("sum=1 cout=1", [5, 8])):
    found = models(hand + [[u] for u in units])
    answer = "SATISFIABLE" if found else "UNSATISFIABLE"
    print(f"units {units}: {text}: {answer}, {len(found)} assignments")
    for bits in found:
        print("  " + " ".join(f"{n}={bits[v - 1]}" for n, v in var.items()))
    assert len(found) == (0 if -1 in units else 1)

# An encoding with a clause missing still looks like an encoding.
extra, flipped = [], 0
for i in range(len(hand)):
    short = hand[:i] + hand[i + 1:]
    extra.append(len(models(short)) - len(rows))
    flipped += bool(models(short + [[5], [8], [-1]]))
print(f"with one clause removed: {min(extra)} to {max(extra)} assignments "
      f"more than the circuit has rows;")
print(f"the first question turns SATISFIABLE for {flipped} of the "
      f"{len(hand)} removals")
assert min(extra) > 0 and flipped > 0
