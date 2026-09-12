# Chapter 6: the template method under both simulators.
EXAMPLE_LANG  := python
TOP           := run_both.sh
SOURCES       := tb_template.sv
PYTHON        := bash
EXPECT_OUTPUT := verdict: the simulators disagree on the template method
LINT_CMD      := verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                     -Wno-DECLFILENAME --top-module tb_template \
                     tb_template.sv \
                     && echo "verilator --lint-only -Wall: no warnings"
include ../../common.mk

clean::
	rm -rf build
