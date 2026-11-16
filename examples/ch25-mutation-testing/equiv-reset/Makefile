# A mutant equivalent only under the tool's reset model: m05, the
# asynchronous reset made synchronous. The miter by bounded search and
# by rIC3, then a Verilator testbench that pulses rst_n between clock
# edges, on the repaired FIFO and on m05 (the source schema). Selects
# ric3-ic3, so it is skipped where rIC3 is not installed. About thirty
# seconds.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := reset.py
SOURCES       := reset.py
PYTHON        := python3 -I -B
LINT_CMD      := python3 -I -B -m py_compile reset.py && \
                 verilator --lint-only --timing --timescale 1ns/1ps -Wall \
                 -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                 --top-module tb_async_reset $(C09)/rtl/fifo_fixed.sv \
                 tb_async_reset.sv && \
                 echo "lint: no warnings"
EXPECT_OUTPUT := verdict: m05 is equivalent to the tool, and a reset pulse
include ../../common.mk
