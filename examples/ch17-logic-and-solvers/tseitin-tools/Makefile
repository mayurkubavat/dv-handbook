# The same full adder through Yosys (and-inverter graph, 9 ANDs), ABC
# (7 ANDs after structural hashing; a file of 14 gate clauses and 4
# unit clauses) and Yosys' SAT pass (40 variables, 100 clauses). Needs
# yosys and yosys-abc; the script prints a line beginning "skipped"
# when either is missing.
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := run_tools.py
SOURCES       := run_tools.py ../common/dimacs.py
EXPECT_OUTPUT := one circuit: 17 clauses by hand
include ../../common.mk
