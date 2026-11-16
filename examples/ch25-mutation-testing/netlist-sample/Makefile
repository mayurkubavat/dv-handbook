# A uniform sample of 1,000 netlist mutations (seed 1), run: a netlist
# holding only those behind one select, the four testbenches built once
# each, kills and Clopper-Pearson intervals at n = 30, 100, 300 and 1000,
# and every sampled verdict checked against the committed population
# file. Yosys and Verilator; about a minute.
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := sample.py
SOURCES       := sample.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: the sample of 1000 reproduces the population run
include ../../common.mk
