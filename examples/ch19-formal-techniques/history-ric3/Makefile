# The k-th word out of the FIFO equals the k-th word in, by a history
# variable and by a prophecy read only where it is checked; both need
# rIC3 (the in-house engines give no verdict). Selects ric3-ic3, so
# it is skipped where rIC3 is not installed. About twenty-five
# seconds.
EXAMPLE_LANG  := informal
REQUIRES      := ric3
TOP           := hist.tcl
SOURCES       := hist.tcl ../common/ch19.tcl ../history/hp.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := proph_top
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: the k-th word proven by history
include ../../common.mk
