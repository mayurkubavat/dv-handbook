# Chapter 1, the random test again in cocotb (for Part V readers).
EXAMPLE_LANG := cocotb
TOP          := fifo
SOURCES      := ../rtl/fifo.sv
TEST_MODULE  := test_fifo_random
EXPECT       := fail      # this test exists to find the bug
# The failure must be the test failing, not the simulator or cocotb
# failing to start; without this a missing tool would count as success.
EXPECT_OUTPUT := TESTS=1 PASS=0 FAIL=1
include ../../common.mk
