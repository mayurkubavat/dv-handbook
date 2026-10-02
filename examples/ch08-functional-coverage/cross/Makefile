# The runner builds with --coverage and reads the cross bins back from
# the database; see run_cross.sh. Needs Verilator 5.050 or later, which
# runs covergroups; Icarus 13.0 rejects the covergroup keyword. lint.vlt
# waives one 5.052 lint artifact.
EXAMPLE_LANG  := python
TOP           := run_cross.sh
SOURCES       := run_cross.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_cross lint.vlt tb_cross.sv \
                 && echo "lint: no warnings (tb_cross_binsof.sv warns" \
                         "COVERIGN by design; the runner shows it)"
EXPECT_OUTPUT := verdict: .dat holds 160 cross bins, 12 hit; binsof was dropped
include ../../common.mk
