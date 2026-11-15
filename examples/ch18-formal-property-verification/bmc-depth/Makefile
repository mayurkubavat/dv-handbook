# Bounded model checking as a method: a counter's bug found at depth
# 17, 65 and 129, and the same `undetermined` row for a true property
# and for a bug the search did not reach. About ten seconds, six of
# them the two limits.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := bmc_depth.tcl
SOURCES       := bmc_depth.tcl deep.sv ../common/proof.tcl
LINT_TOP      := deep
EXPECT_OUTPUT := verdict: a bug at depth 17, 65 and 129
include ../../common.mk
