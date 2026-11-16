# The simulator's initial values are part of the oracle: the seven
# source mutants no testbench killed, and m44, run with the book's flags
# and then with +verilator+rand+reset+2 under seeds 1-5. Writes
# tbl-ch25-survivors.md, with the miter verdicts read from the committed
# run.out of the miter examples. Verilator only; about twenty seconds.
EXAMPLE_LANG  := python
TOP           := randinit.py
SOURCES       := randinit.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: m09, m11 and m13 die with randomized initial values
include ../../common.mk
