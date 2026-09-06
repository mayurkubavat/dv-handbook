# Chapter 1, random test with an independent reference model. Finds the bug.
# Run with a different seed:  make run PLUSARGS=+seed=7
EXAMPLE_LANG := sv
TOP          := tb_fifo_random
SOURCES      := ../rtl/fifo.sv tb_fifo_random.sv
PLUSARGS     := +seed=1
EXPECT       := fail      # this test exists to find the bug
include ../../common.mk
