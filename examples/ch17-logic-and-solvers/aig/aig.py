"""aig.py -- read the full adder as an and-inverter graph.

    python3 aig.py

fa.aag is what Yosys writes for full_adder.sv (the tseitin-tools
example regenerates it). This script decodes the file, checks that
the graph computes the full adder by evaluating it on all eight input
rows, and then shares equal gates the way a tool does while it builds
a graph: structural hashing.
"""
import itertools
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))
import netlist  # noqa: E402
from aiger import Aig, show  # noqa: E402

aig = Aig(HERE / "fa.aag")
print(f"fa.aag: {len(aig.inputs)} inputs, {len(aig.latches)} latches, "
      f"{len(aig.outputs)} outputs, {len(aig.ands)} ANDs, "
      f"largest variable {aig.maxvar}")
for k, lit in enumerate(aig.inputs):
    print(f"  input  {lit:2d}  {show(lit)} = {aig.names[f'i{k}']}")
for out, x, y in aig.ands:
    print(f"  and    {out:2d} {x:2d} {y:2d}  {show(out)} = "
          f"{show(x)} & {show(y)}")
for k, lit in enumerate(aig.outputs):
    print(f"  output {lit:2d}  {aig.names[f'o{k}']} = {show(lit)}")


def evaluate(aig, row):
    """The value of every output for one row of input values."""
    val = {0: 0}
    val.update({lit >> 1: bit for lit, bit in zip(aig.inputs, row)})
    for out, x, y in aig.ands:          # the file lists inputs first
        val[out >> 1] = ((val[x >> 1] ^ (x & 1)) & (val[y >> 1] ^ (y & 1)))
    return [val[lit >> 1] ^ (lit & 1) for lit in aig.outputs]


inputs, gates = netlist.read(HERE.parent / "truth-table" / "full_adder.sv")
agree = 0
for row in itertools.product((0, 1), repeat=len(inputs)):
    want = netlist.evaluate(inputs, gates, row)
    agree += evaluate(aig, row) == [want["sum"], want["cout"]]
print(f"the graph and full_adder.sv agree on {agree} of 8 input rows")
assert agree == 8


def strash(ands):
    """Rebuild the gates through a table keyed on the two inputs."""
    table, rename, kept = {}, {}, []

    def new(lit):                       # a literal after renaming
        return rename.get(lit & ~1, lit & ~1) | (lit & 1)

    for out, x, y in ands:
        key = tuple(sorted((new(x), new(y))))
        if key in table:
            rename[out] = table[key]    # an equal gate exists: reuse it
        else:
            table[key] = out
            kept.append((out,) + key)
    return kept, rename


kept, rename = strash(aig.ands)
print(f"structural hashing: {len(aig.ands)} ANDs -> {len(kept)} ANDs")
for dup, orig in rename.items():
    print(f"  {show(dup)} is the same gate as {show(orig)}")
assert (len(aig.ands), len(kept)) == (9, 7)
n = len(kept)
print(f"as clauses, three for each AND: {len(aig.inputs) + n} variables, "
      f"{3 * n} clauses")
