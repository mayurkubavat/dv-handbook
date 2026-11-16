# Assumption sanity on a counter with a mode: an assumption that ends
# every trace, caught by any cover, and one that ends only the mode-1
# traces, which a deep cover passes and only the assertion's witness
# cover catches. Under a second.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := sanity.tcl
SOURCES       := sanity.tcl ../common/ch19.tcl sanity.sv
LINT_TOP      := sanity
EXPECT_OUTPUT := verdict: the deep cover passes the partial dead end
include ../../common.mk
