# Version 1's own test, ported: eight words from 0x1000 to 0x2000 with
# the original testbench's slave (READY one cycle after VALID).
EXAMPLE_LANG  := sv
TOP           := tb_v1
SOURCES       := ../tb/lint.vlt ../rtl/dma_regs_pkg.sv ../tb/dma_ifs.sv \
                 ../tb/dma_tb_pkg.sv ../rtl/dma_v1.v ../tb/tb_v1.sv
PLUSARGS      := +test=directed +verbose
EXPECT_OUTPUT := result: PASS
include ../../common.mk
