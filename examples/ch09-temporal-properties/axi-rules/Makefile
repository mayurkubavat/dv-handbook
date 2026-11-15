# The AXI handshake rules as clocked assertions on the DMA of the case
# study, bound into its random test on Verilator and seen to fail on
# two mutants; see run_axi.sh.
C11           := ../../ch11-architecture-to-verification
EXAMPLE_LANG  := python
TOP           := run_axi.sh
SOURCES       := run_axi.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT \
                     -Wno-SYNCASYNCNET --top-module tb_v2 \
                     $(C11)/tb/lint.vlt $(C11)/rtl/dma_regs_pkg.sv \
                     $(C11)/tb/dma_ifs.sv $(C11)/tb/dma_tb_pkg.sv \
                     $(C11)/rtl/dma_v2.sv axil_master_sva.sv dma_bind.sv \
                     $(C11)/tb/tb_v2.sv && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: no rule failed on the design
include ../../common.mk
