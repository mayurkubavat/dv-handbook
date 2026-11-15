# The full adder as 17 clauses: written by hand, built by the
# chapter's gate-by-gate encoder, and checked against the truth table
# by trying all 256 assignments.
EXAMPLE_LANG  := python
TOP           := encode.py
SOURCES       := encode.py ../common/dimacs.py ../common/netlist.py \
                 ../common/tseitin.py
EXPECT_OUTPUT := the same set of clauses: True
include ../../common.mk
