# The FIFO checker mirrored as a cocotb monitor, on Icarus, which runs
# no concurrent assertion. `make run` runs the test on the repaired
# FIFO, which must pass, and then on the original FIFO of the first
# chapter with FIFO_EXPECT=bug, where the test requires the monitor to
# fail it on FullBackward_A alone; the second run has a build directory
# of its own, so neither reuses the other's compiled design.
EXAMPLE_LANG  := cocotb
TOP           := fifo
SOURCES       := ../rtl/fifo_fixed.sv
TEST_MODULE   := test_fifo_monitor
EXPECT_OUTPUT := the monitor failed the original FIFO, as required
ORIGINAL      := ../../ch01-what-is-dv/rtl/fifo.sv
include ../../common.mk

run:
	@echo "=== the same monitor on the original FIFO"
	@FIFO_EXPECT=bug $(MAKE) --no-print-directory sim \
	    SOURCES=$(ORIGINAL) SIM_BUILD=$(BUILD_DIR)/original \
	    COCOTB_RESULTS_FILE=$(BUILD_DIR)/original.xml \
	    >$(BUILD_DIR)/original.log 2>&1 \
	    || { tail -20 $(BUILD_DIR)/original.log; exit 1; }
	@sed -nE 's/^.* cocotb\.fifo +/  /p' $(BUILD_DIR)/original.log
	@grep -q 'TESTS=1 PASS=1 FAIL=0' $(BUILD_DIR)/original.log
	@echo "the monitor failed the original FIFO, as required"
