# History and prophecy variables, in-house: bounded $past refuted on a
# correct unit, a one-bit history variable proven and its mutant
# refuted, and a prophecy asserted where it is guessed, refuted at
# depth 1 on a correct FIFO by a trace that ends before the check.
# Under two seconds.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := hist.tcl
SOURCES       := hist.tcl ../common/ch19.tcl hp.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := proph_top
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: the history bit proves what three cycles
include ../../common.mk
