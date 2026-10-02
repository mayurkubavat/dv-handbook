# The runner builds two testbenches and runs each with sampling on and
# off; see run_illegal.sh. Needs Verilator 5.050 or later, which runs
# covergroups; Icarus 13.0 rejects the covergroup keyword. lint.vlt waives
# one 5.052 lint artifact.
EXAMPLE_LANG  := python
TOP           := run_illegal.sh
SOURCES       := run_illegal.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_illegal lint.vlt tb_illegal.sv \
                 && verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_ignore_assert lint.vlt \
                     tb_ignore_assert.sv \
                 && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the illegal bin needs sampling; the assertion does not
include ../../common.mk
