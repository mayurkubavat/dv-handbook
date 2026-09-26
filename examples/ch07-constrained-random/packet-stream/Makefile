# The runner builds once and runs under three seeds; see run_stream.sh.
# Runs on Verilator with the z3 solver on the path (the book's `dvbook`
# environment); Icarus 13.0 has no randomize().
EXAMPLE_LANG  := python
TOP           := run_stream.sh
SOURCES       := run_stream.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     --top-module tb_packet_stream \
                     ../../ch01-what-is-dv/rtl/fifo.sv \
                     ../../ch06-oop-testbench-design/fifo-env/fifo_if.sv \
                     ../../ch06-oop-testbench-design/fifo-env/env.sv \
                     rand_packet.sv tb_packet_stream.sv \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: every packet checked
include ../../common.mk
