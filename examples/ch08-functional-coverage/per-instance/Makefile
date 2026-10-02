# Needs Verilator 5.050 or later, which runs covergroups; Icarus 13.0
# rejects the covergroup keyword. lint.vlt waives two 5.052 lint artifacts.
EXAMPLE_LANG  := sv
TOP           := tb_per_instance
SOURCES       := lint.vlt tb_per_instance.sv
EXPECT_OUTPUT := verdict: instances 50.00, 50.00; type 0.00, IEEE says 50 or 100
include ../../common.mk
