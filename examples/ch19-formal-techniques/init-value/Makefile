# Initial-value abstraction on the book's FIFO: a mutant out of reach
# from reset at 256 entries found at depth 1 from the states an
# invariant allows; the correct FIFO proved from those states; the
# two side conditions proved; a weaker start set's unreachable
# counterexample; the full cover from reset and from INV states.
# In-house engines only. About twenty seconds, ten of them two limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := init.tcl
SOURCES       := init.tcl ../common/ch19.tcl iv.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := iv_top
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: a bug 255 pushes deep found at depth 1
include ../../common.mk
