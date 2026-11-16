# Data independence on the book's FIFO: one tracked word chosen by a
# free oracle, with a symbolic value held by $stable; the check out
# of reach of the in-house engines at DEPTH 16 alone, proven with a
# helper that names one memory slot, and a mutant caught. In-house
# engines only. About fifteen seconds, ten of them two limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := track.tcl
SOURCES       := track.tcl ../common/ch19.tcl track.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := track
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: integrity proven through one tracked word
include ../../common.mk
