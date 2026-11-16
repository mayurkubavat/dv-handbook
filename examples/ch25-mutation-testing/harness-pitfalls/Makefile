# Two harness defects: the parallel_case pragma Yosys writes, which
# Verilator turns into an assertion that kills select-bit mutations in a
# testbench with no checker, unless built with --no-assert-case; and a
# +seed= plusarg given twice, of which $value$plusargs reads the first.
# Yosys and Verilator; about twenty seconds.
EXAMPLE_LANG  := python
REQUIRES      := yosys
TOP           := pitfalls.py
SOURCES       := pitfalls.py
PYTHON        := python3 -I -B
LINT_CMD      := python3 -I -B -m py_compile pitfalls.py && \
                 verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                 -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                 --top-module tb_plusarg tb_plusarg.sv && \
                 echo "lint: no warnings"
EXPECT_OUTPUT := verdict: the pragma assertion kills in a checkless testbench
include ../../common.mk
