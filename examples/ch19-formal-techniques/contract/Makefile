# Ghost state and a reference model on the book's FIFO: an occupancy
# count built from the ports, the contract stated on it, proved at
# DEPTH 16 alone and at 64 with a helper that ties the count to the
# FIFO's own. About fifteen seconds, ten of them two limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := contract.tcl
SOURCES       := contract.tcl ../common/ch19.tcl ../common/hier.sv \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv
LINT_TOP      := fifo_ctr
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: the contract proven on its ghost count
include ../../common.mk
