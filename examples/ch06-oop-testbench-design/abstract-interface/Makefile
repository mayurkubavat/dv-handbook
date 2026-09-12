# Chapter 6: an abstract class and two interface classes. Neither compiles
# on Icarus 13.0, so this runs on the default simulator only.
# Verilator 5.030 reports a pure virtual method's name as an undriven
# signal; waived, since a pure virtual method has no body to drive.
VERILATOR_FLAGS := --timing --timescale 1ns/1ps -Wall -Wno-DECLFILENAME \
                   -Wno-UNUSEDSIGNAL -Wno-UNDRIVEN
EXAMPLE_LANG := sv
TOP          := tb_abstract
SOURCES      := tb_abstract.sv
include ../../common.mk
