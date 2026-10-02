# Needs a simulator with covergroups: the book's Verilator 5.052 (support
# arrived in 5.050). Icarus 13.0 rejects the covergroup keyword, so this
# example has no Icarus run. lint.vlt waives two 5.052 lint artifacts.
EXAMPLE_LANG  := sv
TOP           := tb_sampling_forms
SOURCES       := lint.vlt tb_sampling_forms.sv
EXPECT_OUTPUT := verdict: the clocked form counted four idle cycles
include ../../common.mk
