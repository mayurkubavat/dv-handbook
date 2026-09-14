# The runner builds once and runs twice; see run_nosolver.sh.
EXAMPLE_LANG  := python
TOP           := run_nosolver.sh
SOURCES       := run_nosolver.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                     --top-module tb_nosolver tb_nosolver.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: without a solver every call returned 0
include ../../common.mk
