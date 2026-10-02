# The runner builds the counter testbench with --coverage, runs it twice
# and reads the .dat files back with verilator_coverage; see
# run_codecov.sh. Verilator only: Icarus has no coverage database.
EXAMPLE_LANG  := python
TOP           := run_codecov.sh
SOURCES       := run_codecov.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_counter_cov \
                     ../../appF-counter/rtl/counter.sv tb_counter_cov.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: a merge adds counts
include ../../common.mk
