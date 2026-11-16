# Assume-guarantee on two blocks in a ring, each passing the other's
# output on one cycle later: each proved under the other's guarantee,
# a reset-value mutant refuted, the safety ring proven; each live
# under the other's "eventually", the liveness ring refuted with a
# lasso; and the ring with both resets at 1, whose two false lemmas
# are each "proven" with the other assumed. Under a second.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := ag.tcl
SOURCES       := ag.tcl ../common/ch19.tcl ag.sv
LINT_TOP      := ag_top
EXPECT_OUTPUT := verdict: the circular argument holds for safety
include ../../common.mk
