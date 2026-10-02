# Needs Verilator 5.050 or later, which runs covergroups; Icarus 13.0
# rejects the covergroup keyword. lint.vlt waives one 5.052 lint artifact.
EXAMPLE_LANG  := sv
TOP           := tb_percentage
SOURCES       := lint.vlt tb_percentage.sv
EXPECT_OUTPUT := verdict: tool 50.00 (3 of 6 bins); standard's average 62.50
include ../../common.mk
