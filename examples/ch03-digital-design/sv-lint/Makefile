# Chapter 3: what lint sees in the two-clock design, and what it cannot.
#
# Verilator's strictest lint passes this design in silence. The design has an
# eight-bit clock-domain crossing with no synchronizer. Section 3.8 runs the
# book's own tool over the same files and reads what lint could not say.
#
# There is no testbench here on purpose: the example is the static check.
EXAMPLE_LANG := sv
TOP          := top
SOURCES      := ../rtl/regblock.sv ../rtl/sync2.sv \
                ../rtl/datapath.sv ../rtl/top.sv
LINT_ONLY    := 1
include ../../common.mk
