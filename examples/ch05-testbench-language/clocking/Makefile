# Chapter 5: a clocking block. Unsupported on Icarus 13.0, so this runs on
# the default simulator only.
# Verilator 5.030 reports a clocking block's `input` as an undriven
# signal, although it is the sampled copy of a driven one; waived here.
VERILATOR_FLAGS := --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
                   -Wno-UNUSEDSIGNAL -Wno-UNDRIVEN
EXAMPLE_LANG := sv
TOP          := tb_clocking
SOURCES      := tb_clocking.sv
include ../../common.mk
