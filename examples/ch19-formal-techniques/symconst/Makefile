# A symbolic constant two ways on the book's FIFO: $anyconst, which
# leaves the report without its RTL property and with no message,
# and a free input held by $stable, which works; and a check of what
# the assumption says about the reset cycle. A few seconds.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := sc.tcl
SOURCES       := sc.tcl ../common/ch19.tcl sc_free.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := sc_free
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: the anyconst spelling leaves no RTL property
include ../../common.mk
