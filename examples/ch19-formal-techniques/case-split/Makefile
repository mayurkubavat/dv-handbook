# Case split on an 8-bit multiplier miter (outside the chapter's
# spine; a preview of the equivalence chapter): proven whole, proven
# in four cases on the top bits of a with the completeness check, and
# a bug in case 3 that a three-case list would have missed, caught by
# its completeness check. About forty seconds of proof.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := split.tcl
SOURCES       := split.tcl ../common/ch19.tcl mul.sv
LINT_TOP      := mul_miter
EXPECT_OUTPUT := verdict: four cases and their completeness proven
include ../../common.mk
