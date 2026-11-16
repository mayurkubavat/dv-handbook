# The kill matrix: the 44 source mutants of the repaired FIFO against
# the book's four FIFO testbenches, read by path. The source schema is
# built once for each testbench and run 45 times; then m35 under the
# random test's seeds 1-100; then the matrix of the per-mutant builds
# in the committed measure.out is compared with the schema's.
# `MEASURE=1 make run` rewrites measure.out (180 builds, several
# minutes). Verilator only; about fifteen seconds.
EXAMPLE_LANG  := python
TOP           := sim.py
SOURCES       := sim.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: the schema reproduces the per-mutant kill matrix
include ../../common.mk
