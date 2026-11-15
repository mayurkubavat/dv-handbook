# A wrong verdict, measured: on Verilator 5.052 an assertion with goto
# repetition in its consequent reports nothing when the design breaks
# the rule. The hand-built monitor beside it does. If a later release
# reports the failure, this example fails and the chapter's Pitfall is
# out of date.
EXAMPLE_LANG  := sv
TOP           := tb_goto
SOURCES       := tb_goto.sv
EXPECT_OUTPUT := verdict: the simulator missed the failure the monitor saw
include ../../common.mk
