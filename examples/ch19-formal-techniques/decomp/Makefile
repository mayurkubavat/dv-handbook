# Property decomposition on the DMA of the architecture case study:
# an end-to-end property and its two lemmas without a verdict alone,
# by bounded search, induction or IC3 in five seconds, with the
# witness cover reached; the end-to-end property proven from the
# lemmas. In-house engines only. About fifty seconds, forty-five of
# them nine limits.
C11           := ../../ch11-architecture-to-verification
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := decomp.tcl
SOURCES       := decomp.tcl ../common/ch19.tcl dma_wcount.sv \
                 $(C11)/rtl/dma_regs_pkg.sv $(C11)/rtl/dma_v2.sv
LINT_TOP      := dma_v2
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET $(C11)/tb/lint.vlt
EXPECT_OUTPUT := verdict: the chain closes
include ../../common.mk
