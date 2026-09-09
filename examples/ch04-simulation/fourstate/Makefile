# Chapter 4: what four-state finds, what two-state hides, and what
# randomized initialization finds instead.
EXAMPLE_LANG  := python
TOP           := run.sh
SOURCES       := dut_unreset.sv tb_fourstate.sv
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME --top-module tb_fourstate \
                     dut_unreset.sv tb_fourstate.sv && echo "lint: no warnings"
EXPECT_OUTPUT := out is unknown
include ../../common.mk

clean::
	rm -rf build
