# Needs a simulator with covergroups: the book's Verilator 5.052 (support
# arrived in 5.050). Icarus 13.0 rejects the covergroup keyword, so this
# example has no Icarus run. The runner keeps the simulator's abort
# message, which the plain recipe would hide; see run_silent.sh.
EXAMPLE_LANG  := python
TOP           := run_silent.sh
SOURCES       := run_silent.sh tb_silent_group.sv lint.vlt
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_silent_group lint.vlt \
                     tb_silent_group.sv && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: one group said nothing
include ../../common.mk
