# The source-level fault model: the 44 mutants of the repaired FIFO
# made at run time by common/srcmut.py, listed one line each; counts
# by operator and the chapter's operator table (tbl-ch25-operators.md);
# the book's -Wall lint on each single-edit copy; and which mutants
# Yosys cannot tell from the original or from each other. Yosys and
# Verilator; a few seconds.
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := mutants.py
SOURCES       := mutants.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: 44 mutants; lint kills 7; synthesis finds 1
include ../../common.mk
