# Runs on Verilator with the z3 solver on the path (the book's `dvbook`
# environment); Icarus 13.0 has no randomize().
EXAMPLE_LANG := sv
TOP          := tb_forms
SOURCES      := forms.sv tb_forms.sv
# Verilator 5.052 reports a foreach index and the array under `unique` as
# undriven signals; they are constraint expressions, not signals.
VERILATOR_FLAGS := --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
                   -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT -Wno-UNDRIVEN
EXPECT_OUTPUT := every call checked: 0 failures
include ../../common.mk
