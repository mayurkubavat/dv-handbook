# The netlist fault model's population: every mutation Yosys's mutate
# pass lists for the repaired FIFO after prep, its SHA-256, counts by
# mode, cell type and source line, the share on the memory, and a check
# that the numbering matches the committed population file. Yosys only;
# a few seconds.
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := list.py
SOURCES       := list.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: 9281 mutations, 73.8% on the memory
include ../../common.mk
