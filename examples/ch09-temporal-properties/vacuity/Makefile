# A vacuous pass and the cover that exposes it, on Verilator with
# --coverage; see run_vacuity.sh.
EXAMPLE_LANG  := python
TOP           := run_vacuity.sh
SOURCES       := run_vacuity.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_vacuity ack_check.sv responder.sv \
                     tb_vacuity.sv && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: a pass with the cover at zero proved nothing
include ../../common.mk
