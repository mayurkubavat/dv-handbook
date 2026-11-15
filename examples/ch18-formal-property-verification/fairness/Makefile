# Liveness under three environments: the eventual form is refuted
# alone and proved under a fairness assumption; the bounded form is
# still refuted under fairness and needs a bound on the environment.
# Six sessions of one property each; about a second.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := fair.tcl
SOURCES       := fair.tcl ../lasso/live_small.sv ../common/proof.tcl
LINT_TOP      := live_small
EXPECT_OUTPUT := verdict: fairness proves the eventual form only
include ../../common.mk
