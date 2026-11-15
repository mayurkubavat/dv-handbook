# A multi-tick rule as a monitor register and an immediate assertion,
# on Verilator; see run_response.sh.
EXAMPLE_LANG  := python
TOP           := run_response.sh
SOURCES       := run_response.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_responder responder.sv resp_check.sv \
                     tb_responder.sv && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the monitor register caught the late grant
include ../../common.mk
