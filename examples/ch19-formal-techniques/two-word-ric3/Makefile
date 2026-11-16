# The two-word check of two-word/ handed to rIC3 without the slot
# helpers, DEPTH 4: no verdict for the flag form; the two head
# properties of the position form proven and its ordering lemma not.
# Selects ric3-ic3, so it is skipped where rIC3 is not installed.
# About thirty seconds, most of them limits.
EXAMPLE_LANG  := informal
REQUIRES      := ric3
TOP           := ric3.tcl
SOURCES       := ric3.tcl ../common/ch19.tcl ../two-word/two_word.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := two_word
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: without the slot helpers rIC3 proves neither
include ../../common.mk
