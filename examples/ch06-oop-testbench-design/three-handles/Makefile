# Chapter 6: one object, three handles. A comparison across both
# simulators; the verdict line is pinned so a missing tool fails the run.
EXAMPLE_LANG  := python
TOP           := run_both.sh
SOURCES       := tb_three_handles.sv
PYTHON        := bash
EXPECT_OUTPUT := verdict: the simulators disagree on one virtual call
LINT_CMD      := verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                     -Wno-DECLFILENAME --top-module tb_three_handles \
                     tb_three_handles.sv \
                     && echo "verilator --lint-only -Wall: no warnings"
include ../../common.mk

clean::
	rm -rf build
