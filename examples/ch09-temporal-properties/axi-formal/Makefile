# The AXI master rules proved on the DMA engine with InFormal,
# three mutants caught, and one spelling of a rule that the tool's reset
# model refutes on a correct design; see axi.tcl.
C11           := ../../ch11-architecture-to-verification
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := axi.tcl
SOURCES       := axi.tcl $(C11)/rtl/dma_regs_pkg.sv $(C11)/rtl/dma_v2.sv \
                 ../axi-rules/axil_master_sva.sv ../axi-rules/dma_bind.sv
LINT_TOP      := dma_v2
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET $(C11)/tb/lint.vlt
EXPECT_OUTPUT := verdict: six rules proved
include ../../common.mk
