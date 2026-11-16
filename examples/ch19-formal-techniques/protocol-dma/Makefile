# hs_rules (from protocol/) bound five times on the DMA of the
# architecture case study: the six AXI master rules proved under the
# slave's rules by informal-ic3, and a property about the read
# response that fails with the slave free and holds once its rules
# are assumed. In-house engines only. A few seconds.
C11           := ../../ch11-architecture-to-verification
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := dma.tcl
SOURCES       := dma.tcl ../common/ch19.tcl ../protocol/hs_rules.sv \
                 $(C11)/rtl/dma_regs_pkg.sv $(C11)/rtl/dma_v2.sv \
                 r_first.sv dma_master_bind.sv \
                 dma_slave_bind.sv
LINT_TOP      := dma_v2
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET $(C11)/tb/lint.vlt
EXPECT_OUTPUT := verdict: the master rules hold under the slave's
include ../../common.mk
