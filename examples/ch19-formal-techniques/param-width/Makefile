# Parameter reduction on the book's FIFO: Chapter 1's bug found at
# DEPTH 4 and at 16, a five-bit count proved at 16 and refuted at 32,
# and pointers proved at DEPTH 4 and 8 and refuted at 5. A few
# seconds.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := width.tcl
SOURCES       := width.tcl ../common/ch19.tcl pw_top.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := pw_top
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: a counterexample at DEPTH 4 is the bug at 16
include ../../common.mk
