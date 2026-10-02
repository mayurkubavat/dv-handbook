# Needs a simulator with covergroups: the book's Verilator 5.052 (support
# arrived in 5.050). Icarus 13.0 rejects the covergroup keyword, so this
# example has no Icarus run. The runner builds with --coverage itself
# and reads the bins back from the database; see run_bins.sh.
EXAMPLE_LANG  := python
TOP           := run_bins.sh
SOURCES       := run_bins.sh tb_bins_kinds.sv lint.vlt
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_bins_kinds lint.vlt tb_bins_kinds.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the standard says 100.00
include ../../common.mk
