# The full adder as an and-inverter graph in the AIGER text format:
# decoded line by line, checked against the SystemVerilog on all eight
# rows, and reduced from 9 ANDs to 7 by structural hashing.
EXAMPLE_LANG  := python
TOP           := aig.py
SOURCES       := aig.py ../common/aiger.py ../common/netlist.py
EXPECT_OUTPUT := structural hashing: 9 ANDs -> 7 ANDs
include ../../common.mk
