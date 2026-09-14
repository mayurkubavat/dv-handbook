# The runner runs the binary under several seeds; see run_seeds.sh.
EXAMPLE_LANG  := python
TOP           := run_seeds.sh
SOURCES       := run_seeds.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL --top-module tb_seeds \
                     tb_seeds.sv && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the run's seed reproduces the run
include ../../common.mk
