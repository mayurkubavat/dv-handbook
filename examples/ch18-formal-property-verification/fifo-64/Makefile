# The chapter's procedure on a FIFO of 64 entries: witness covers, a
# bounded search, induction and IC3 without a verdict in five seconds,
# the external engine with one, the helper proved and then assumed,
# and the covers again. Selects ric3-ic3, so it is skipped where rIC3
# is not installed. About twenty seconds, thirteen of them limits.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := informal
REQUIRES      := ric3
TOP           := fifo64.tcl
SOURCES       := fifo64.tcl ../common/proof.tcl $(C09)/rtl/fifo_fixed.sv
LINT_TOP      := fifo
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: proven with one helper, itself proven
include ../../common.mk
