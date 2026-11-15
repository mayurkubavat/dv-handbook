# The FIFO's occupancy logic unrolled at the word level with z3: the
# bug appears 15 steps after reset; the repaired design shows nothing
# within 20. Needs the z3 Python package; without it the script prints
# a line beginning "skipped".
EXAMPLE_LANG  := python
TOP           := unroll_z3.py
SOURCES       := unroll_z3.py
EXPECT_OUTPUT := no counterexample within 20 steps of reset
include ../../common.mk
