# The pointer property and its helper at 2, 4, 8 and 64 entries under
# induction, IC3 and the external engine rIC3, and the property again
# with the helper assumed: a grid of verdicts. Selects ric3-ic3, so it
# is skipped where rIC3 is not installed. About half a minute, most of
# it five limits of five seconds.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := informal
REQUIRES      := ric3
TOP           := scaling.tcl
SOURCES       := scaling.tcl ../common/proof.tcl $(C09)/rtl/fifo_fixed.sv
LINT_TOP      := fifo
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: with the helper assumed, every engine proves
include ../../common.mk
