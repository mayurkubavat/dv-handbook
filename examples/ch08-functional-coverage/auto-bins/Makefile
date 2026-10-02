# Needs a simulator with covergroups: the book's Verilator 5.052 (support
# arrived in 5.050). Icarus 13.0 rejects the covergroup keyword, so this
# example has no Icarus run. lint.vlt waives one 5.052 lint artifact.
EXAMPLE_LANG  := sv
TOP           := tb_auto_bins
SOURCES       := lint.vlt tb_auto_bins.sv
EXPECT_OUTPUT := verdict: eight bins where sixty-four were meant
include ../../common.mk
