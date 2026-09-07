# Chapter 3: what lint sees in the two-clock design, and what it cannot.
#
# Verilator's strictest lint passes this design in silence. The design has an
# eight-bit clock-domain crossing with no synchronizer. The chapter's worked
# example runs the book's own tool over the same files and reads what lint
# could not say.
#
# There is no testbench here on purpose: the example is the static check.
#
# This example drops the -Wno-* waivers the shared recipe uses to keep UVM
# source from failing lint, and turns on the two crossing-adjacent warnings
# Verilator leaves off by default. Nothing here is waived, so a silent run
# is the strongest form of the section's point.
EXAMPLE_LANG := sv
VERILATOR_FLAGS := --timing --timescale 1ns/1ps -Wall \
                   -Wwarn-SYNCASYNCNET -Wwarn-IMPERFECTSCH
TOP          := top
SOURCES      := ../rtl/regblock.sv ../rtl/sync2.sv \
                ../rtl/datapath.sv ../rtl/top.sv
LINT_ONLY    := 1
include ../../common.mk
