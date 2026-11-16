# The two-word ordering check on the book's FIFO at DEPTH 4, in-house:
# the position form out of reach alone, proven with helpers that name
# the slot of each tracked word; under them the flag form's ordering
# proven and its once-only checks still without a verdict; a mutant
# that reads a word twice caught by every property. About thirty
# seconds, most of it limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := two.tcl
SOURCES       := two.tcl ../common/ch19.tcl two_word.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := two_word
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: order proven by position with slot helpers
include ../../common.mk
