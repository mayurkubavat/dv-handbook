# Chapter 4: why a monitor reports a value that is correct and old.
#
# Four-state and event-driven, so Icarus: the first read at the edge shows
# x before any edge has happened, which a two-state tool cannot show.
EXAMPLE_LANG  := python
TOP           := run.sh
SOURCES       := tb_sampling.sv
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME --top-module tb_sampling \
                     tb_sampling.sv && echo "lint: no warnings"
EXPECT_OUTPUT := at the edge : q=10
include ../../common.mk

clean::
	rm -rf build
