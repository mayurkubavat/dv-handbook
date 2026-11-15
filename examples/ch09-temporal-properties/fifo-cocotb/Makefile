# The FIFO checker mirrored as a cocotb monitor, on Icarus, which runs
# no concurrent assertion. The design is the repaired FIFO; point
# SOURCES at ../../ch01-what-is-dv/rtl/fifo.sv to watch the monitor
# fail the original.
EXAMPLE_LANG  := cocotb
TOP           := fifo
SOURCES       := ../rtl/fifo_fixed.sv
TEST_MODULE   := test_fifo_monitor
EXPECT_OUTPUT := TESTS=1 PASS=1 FAIL=0
include ../../common.mk
