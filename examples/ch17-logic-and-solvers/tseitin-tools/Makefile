# The same full adder through Yosys (and-inverter graph, 9 ANDs), ABC
# (7 ANDs after structural hashing; 8 variables, 17 clauses) and Yosys'
# SAT pass (40 variables, 100 clauses). Needs yosys and yosys-abc; the
# script prints a line beginning "skipped" when either is missing.
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := run_tools.py
SOURCES       := run_tools.py
EXPECT_OUTPUT := one circuit: 17 clauses by hand
include ../../common.mk
