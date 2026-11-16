# The flat comparison for mem-abs: the whole RAM proved by rIC3, with
# no abstraction, at 16 and 256 words. Selects ric3-ic3, so it is
# skipped where rIC3 is not installed. About ten seconds.
EXAMPLE_LANG  := informal
REQUIRES      := ric3
TOP           := flat.tcl
SOURCES       := flat.tcl ../common/ch19.tcl ../mem-abs/mem_abs.sv
LINT_TOP      := mem_top
EXPECT_OUTPUT := verdict: the flat design proven by rIC3
include ../../common.mk
