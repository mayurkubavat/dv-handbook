# Hierarchical proof on a pipe of two FIFOs, DEPTH 16: each FIFO boxed
# under its contract, the parent's properties without a verdict by
# induction, a spurious counterexample under half the contract, and
# both proven with one parent helper stated on the ghost counts.
# In-house engines only. About fifteen seconds, ten of them limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := hier.tcl
SOURCES       := hier.tcl ../common/ch19.tcl ../common/hier.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := pipe2
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: the boxed pipe proven with its children
include ../../common.mk
