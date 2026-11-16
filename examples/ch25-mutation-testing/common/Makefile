# The chapter's shared Python: mutlib.py (the book's four FIFO
# testbenches, a Verilator runner, verdicts, tool versions),
# srcmut.py (the 44 source mutants and the source schema), yosysmut.py
# (Yosys netlist mutations: list, uniform sample, select netlist) and
# miter.py (InFormal miters and the property set). make run runs the
# self-test. Verilator only; about fifteen seconds.
EXAMPLE_LANG  := python
TOP           := selftest.py
SOURCES       := selftest.py mutlib.py srcmut.py yosysmut.py miter.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := self-test: the shared library holds
include ../../common.mk
