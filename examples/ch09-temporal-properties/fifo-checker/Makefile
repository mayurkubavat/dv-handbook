# The worked example: a FIFO checker written as clocked immediate
# assertions, bound to the design and simulated on Verilator; see
# run_checker.sh.
EXAMPLE_LANG  := python
TOP           := run_checker.sh
SOURCES       := run_checker.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     -Wno-SYNCASYNCNET --top-module tb_fifo_sva \
                     ../rtl/fifo_fixed.sv fifo_sva.sv fifo_bind.sv \
                     tb_fifo_sva.sv && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the repaired FIFO passes with every cover hit
include ../../common.mk
