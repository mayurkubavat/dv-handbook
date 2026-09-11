# Chapter 4: a delay finer than its module's declared precision.
#
# Runs on both simulators, because the finding is that they disagree.
EXAMPLE_LANG  := python
TOP           := run.sh
SOURCES       := coarse.sv fine.sv tb_timescale.sv
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing \
                     -Wno-DECLFILENAME -Wno-STMTDLY \
                     --top-module tb_timescale \
                     coarse.sv fine.sv tb_timescale.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := after #1.4
include ../../common.mk

clean::
	rm -rf build
