# The runner builds once with --coverage, runs two stimulus mixes under
# one seed, merges the two .dat files and reads the bins back; see
# run_fifo_cov.sh. Verilator only: Icarus 13.0 rejects covergroups.
EXAMPLE_LANG  := python
TOP           := run_fifo_cov.sh
SOURCES       := run_fifo_cov.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_fifo_cov lint.vlt \
                     ../../ch01-what-is-dv/rtl/fifo.sv tb_fifo_cov.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the merge closed the hole run A left
include ../../common.mk
