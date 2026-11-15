"""run_unroll.py -- bounded model checking by hand, twice.

    python3 run_unroll.py

Unrolls the counter's and the FIFO's AIGER models with bmc_aag.py,
then reads the FIFO's registers back out of the satisfying
assignment, frame by frame. The two .aag files are written by the
counter-model and fifo-model examples and kept under version control,
so this example needs nothing but Python.
"""
import pathlib

from bmc_aag import bmc

HERE = pathlib.Path(__file__).parent
conflicts = []                          # the last column, bound by bound


def report(line):
    print(line)
    if line.split()[0].isdigit():
        conflicts.append(int(line.split()[-1]))


print("1. the counter: counter.aag")
k, u, model = bmc(HERE / "counter.aag", 10, report)
assert k == 6 and (u.nvars, len(u.clauses) + 1) == (141, 401)
assert conflicts == [1, 1, 1, 1, 2, 6, 0], conflicts

print("2. the FIFO: fifo_bmc.aag")
del conflicts[:]
k, u, model = bmc(HERE / "fifo_bmc.aag", 20, report)
assert k == 16 and (u.nvars, len(u.clauses) + 1) == (1795, 5221)
assert conflicts == [1, 1, 1, 1, 2, 5, 13, 23, 33, 44, 58, 76, 99, 124,
                     152, 185, 195], conflicts
per_frame = (len(u.aig.inputs) + len(u.aig.ands),
             3 * len(u.aig.ands) + len(u.aig.constraints))
print(f"each further frame adds {per_frame[0]} variables and "
      f"{per_frame[1]} clauses")

# The file has no names. The latches are in the order of the model's
# state bits that the property depends on: started, occ[0..4],
# count[0..3]; the inputs are rst_n, wr_en, rd_en.
latch = [row[0] for row in u.aig.latches]
OCC, COUNT = latch[1:6], latch[6:10]
RST_N, WR_EN, _ = u.aig.inputs


def bit(t, lit):
    return int(u.lit(t, lit) in model)


def word(t, lits):
    return sum(bit(t, lit) << i for i, lit in enumerate(lits))


print("3. the counterexample, read from the satisfying assignment")
print("frame  rst_n  count  occ")
for t in range(k + 1):
    rst_n, count, occ = bit(t, RST_N), word(t, COUNT), word(t, OCC)
    if t == 0:                          # registers are not yet reset
        assert rst_n == 0
        print(f"{t:5d}  {rst_n:5d}      -    -")
        continue
    print(f"{t:5d}  {rst_n:5d}  {count:5d}  {occ:3d}")
    # Fifteen pushes are the only way from 0 to 15 in fifteen steps,
    # so these values are forced, whatever solver found the model.
    assert rst_n == 1 and count == occ == t - 1
    assert t == k or bit(t, WR_EN) == 1
print(f"frame {k}: count is 15, so full is high, and occ is 15, not 16")
