# The full adder the chapter encodes, and its truth table by brute
# force: eight rows, and the row counts that rule the method out.
# Lint checks the SystemVerilog with Verilator and the script with
# Python.
EXAMPLE_LANG  := python
TOP           := truth.py
SOURCES       := truth.py ../common/netlist.py
LINT_CMD      := verilator --lint-only -Wall full_adder.sv \
                 && python3 -m py_compile $(SOURCES)
EXPECT_OUTPUT := agree on 8 of 8 rows
include ../../common.mk
