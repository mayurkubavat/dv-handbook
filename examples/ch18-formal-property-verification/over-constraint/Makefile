# Assumptions as constraints: a false assertion, refuted at depth 202
# with no assumption, is `proven` under an over-constraint and under
# two contradictions, and `undetermined` when the engine can only
# search. About ten seconds, eight of them the limits of the last
# block.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := assume.tcl
SOURCES       := assume.tcl handshake.sv ../common/proof.tcl
LINT_TOP      := handshake
EXPECT_OUTPUT := verdict: a false assertion proven under each of three
include ../../common.mk
