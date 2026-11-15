# The bounded-response checker under InFormal: the rule proved on the
# correct responder, and the shortest late grant found on the other;
# see response.tcl.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := response.tcl
SOURCES       := response.tcl ../bounded-response/responder.sv \
                 ../bounded-response/resp_check.sv \
                 ../bounded-response/resp_bind.sv
LINT_TOP      := responder
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL
EXPECT_OUTPUT := verdict: proved on one responder
include ../../common.mk
