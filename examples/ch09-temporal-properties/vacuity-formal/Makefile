# The vacuity example's checker under InFormal: a counterexample with
# free inputs, a vacuous proof under an assumption that is too strong,
# and contradictory assumptions that prove everything; see vacuity.tcl.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := vacuity.tcl
SOURCES       := vacuity.tcl ../vacuity/ack_check.sv ../vacuity/responder.sv
LINT_TOP      := responder
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL
EXPECT_OUTPUT := verdict: an assertion proved under assumptions
include ../../common.mk
