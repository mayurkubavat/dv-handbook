# Runs on Verilator with the z3 solver on the path (the book's `dvbook`
# environment); Icarus 13.0 has no randomize().
EXAMPLE_LANG := sv
TOP          := tb_randomize_check
SOURCES      := tb_randomize_check.sv
EXPECT_OUTPUT := the unchecked call left a stale value; checked calls: 1
include ../../common.mk
