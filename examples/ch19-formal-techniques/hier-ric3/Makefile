# The comparison for hier/: the pipe of two FIFOs at DEPTH 16 proved
# by rIC3 without the parent helper, boxed and flat. Selects ric3-ic3,
# so it is skipped where rIC3 is not installed. A few seconds.
EXAMPLE_LANG  := informal
REQUIRES      := ric3
TOP           := ric3.tcl
SOURCES       := ric3.tcl ../common/ch19.tcl ../common/hier.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := pipe2
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: rIC3 proves the pipe boxed and flat
include ../../common.mk
