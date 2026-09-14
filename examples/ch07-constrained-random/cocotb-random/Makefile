# Runs on Icarus: the stimulus is Python's, and no solver is involved.
# cocotb.mk exports COCOTB_RANDOM_SEED=1 so that the log is reproducible;
# run with COCOTB_RANDOM_SEED=<n> make run to draw a different stream.
EXAMPLE_LANG := cocotb
TOP          := fifo
SOURCES      := ../../ch01-what-is-dv/rtl/fifo.sv
TEST_MODULE  := test_stream
EXPECT_OUTPUT := 0 mismatches
include ../../common.mk
