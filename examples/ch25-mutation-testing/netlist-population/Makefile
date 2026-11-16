# The whole netlist population from the committed pop.tsv: kill rates,
# the random test's seed curve, nested uniform samples with intervals,
# the coverage and width of the interval over 2,000 samples, and rates
# by mode. `MEASURE=1 make run` regenerates pop.tsv (every mutation
# behind one select; Yosys and Verilator, a few minutes) and writes
# measure.out. Python only by default; about thirty seconds.
EXAMPLE_LANG  := python
TOP           := pop.py
SOURCES       := pop.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: the population rates are known
include ../../common.mk
