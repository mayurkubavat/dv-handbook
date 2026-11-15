"""truth.py -- the full adder's truth table, by trying every input.

    python3 truth.py

Reads the five gates from full_adder.sv, evaluates them on all eight
input rows, and uses the table to settle a question of equivalence:
is the carry "g | t" the same function as "at least two of a, b, cin"?
"""
import itertools
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
import netlist  # noqa: E402

inputs, gates = netlist.read(HERE / "full_adder.sv")
print(f"{len(inputs)} inputs, {len(gates)} gates:")
print("  " + ", ".join(f"{out} = {x} {op} {y}" for out, op, x, y in gates))
print("a b cin | p g t | sum cout | majority")
agree = 0
for row in itertools.product((0, 1), repeat=len(inputs)):
    s = netlist.evaluate(inputs, gates, row)
    maj = int(s["a"] + s["b"] + s["cin"] >= 2)
    agree += s["cout"] == maj
    assert s["a"] + s["b"] + s["cin"] == 2 * s["cout"] + s["sum"]
    print(f"{s['a']} {s['b']} {s['cin']}   | {s['p']} {s['g']} {s['t']} |"
          f" {s['sum']}   {s['cout']}    | {maj}")
rows = 2 ** len(inputs)
print(f"cout and the majority of a, b, cin agree on {agree} of {rows} rows")
assert agree == rows, "the two carry forms differ"
print("rows a truth table needs, by number of inputs:")
for n in (3, 16, 32, 64):
    print(f"  {n:2d} inputs  {2 ** n:,}")
