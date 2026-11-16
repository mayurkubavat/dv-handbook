# A protocol checker used as assertion and as assumption: hs_rules, a
# new file derived from Chapter 9's hs_check with a ROLE parameter, on
# a valid/ready stage. The wire stage keeps the rules only when its
# input does; the register stage keeps them anyway; the checker bound
# with the wrong role proves a false rule about the input, and a cover
# shows it. Under two seconds.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := proto.tcl
SOURCES       := proto.tcl ../common/ch19.tcl hs_rules.sv vr.sv
LINT_TOP      := vr_top
EXPECT_OUTPUT := verdict: the role decides which rules bind
include ../../common.mk
