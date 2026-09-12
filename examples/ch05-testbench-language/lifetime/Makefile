# Chapter 5: automatic and static lifetime, under both simulators, because
# whether a static task's two callers corrupt each other depends on how
# the simulator interleaves them and the two tools answer differently.
EXAMPLE_LANG  := python
TOP           := run_both.sh
SOURCES       := tb_lifetime.sv
PYTHON        := bash
EXPECT_OUTPUT := verdict: the static task's answer depends on the simulator
LINT_CMD      := verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                     -Wno-DECLFILENAME --top-module tb_lifetime tb_lifetime.sv \
                     && echo "verilator --lint-only -Wall: no warnings"
include ../../common.mk

clean::
	rm -rf build
