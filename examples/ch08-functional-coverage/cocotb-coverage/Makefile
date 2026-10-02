# The FIFO coverage model in Python with cocotb-coverage, on Icarus,
# where no SystemVerilog covergroup can run. Needs `pip install
# cocotb-coverage` in the book's `dvbook` environment. cocotb.mk exports
# COCOTB_RANDOM_SEED=1 and the test seeds Python's random itself.
EXAMPLE_LANG  := cocotb
TOP           := fifo
SOURCES       := ../../ch01-what-is-dv/rtl/fifo.sv
TEST_MODULE   := test_fifo_cov
EXPECT_OUTPUT := verdict: the push-biased phase closed every bin
include ../../common.mk
