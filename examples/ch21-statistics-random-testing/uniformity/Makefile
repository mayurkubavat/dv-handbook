# Is the generator delivering the distribution? Goodness-of-fit tests
# on the constrained-random chapter's printed counts, read from its
# run.out files by path, then on 2000 fresh draws from six of its
# classes (forms.sv and rand_packet.sv compiled by path), a Python
# control and the power of a bit test. Writes tbl-ch21-uniform.md (kept
# under version control like run.out). Needs Verilator 5.052 with z3 on
# the PATH, as that chapter's examples do; about 40 seconds.
C6            := ../../ch06-oop-testbench-design/fifo-env
C7            := ../../ch07-constrained-random
EXAMPLE_LANG  := python
TOP           := run_draws.sh
SOURCES       := run_draws.sh tb_draws.sv ch07_counts.py uniform.py
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     -Wno-UNDRIVEN --top-module tb_draws \
                     $(C6)/fifo_if.sv $(C6)/env.sv \
                     $(C7)/packet-stream/rand_packet.sv \
                     $(C7)/constraint-forms/forms.sv \
                     tb_draws.sv && python3 -I -B -m py_compile \
                     ch07_counts.py uniform.py && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: solve...before drew s = 1 in 0 of 2000
include ../../common.mk
