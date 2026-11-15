# The valid/ready rule as clocked immediate assertions with $past; see
# run_handshake.sh. Icarus 13.0 compiles $past and then cannot load
# it, so the example is built with the other simulator only.
EXAMPLE_LANG  := python
TOP           := run_handshake.sh
SOURCES       := run_handshake.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_handshake hs_check.sv tb_handshake.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: three rules failed once each
include ../../common.mk
