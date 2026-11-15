# Assumptions as constraints on free inputs: a handshake sink that is
# correct only against a source that keeps the rules, with properties
# in the RTL, in a bound checker and in the script; see assume.tcl.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := assume.tcl
SOURCES       := assume.tcl hs_sink.sv ../handshake/hs_check.sv hs_bind.sv
LINT_TOP      := hs_sink
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: the sink is correct against a source
include ../../common.mk
