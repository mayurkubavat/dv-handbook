# The miter refutes: each of the 44 source mutants against the repaired
# FIFO by bounded model checking, 10 s each; 37 differ, with the depth of
# the shortest distinguishing trace, two are refused by the front end,
# and five stay undecided. Then rd_data compared on every cycle, the
# original against itself. In-house engines only; about twenty seconds.
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := differ.py
SOURCES       := differ.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: 37 mutants differ; bounded search decides none
include ../../common.mk
