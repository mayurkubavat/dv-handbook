# The worked example: a pipe of two 256-entry FIFOs whose two control
# properties induction cannot prove whole, proved through black
# boxes, the children's contracts with a ghost helper, and one parent
# helper; with witness covers first, a mutant child caught, and the
# record printed last. In-house engines only. About seventy seconds.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := pipe.tcl
SOURCES       := pipe.tcl ../common/ch19.tcl ../common/hier.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := pipe2
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: P1 and P2 proven at 256 entries by induction
include ../../common.mk
