# One cover under three engines on two FIFOs: `covered` at depth 17
# from each engine on the repaired design; on the first chapter's,
# `unreachable` from the two engines that prove and `undetermined`
# from bounded search. About five seconds.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := cover.tcl
SOURCES       := cover.tcl ../common/proof.tcl $(C09)/rtl/fifo_fixed.sv \
                 $(C09)/fifo-checker/fifo_sva.sv \
                 $(C09)/fifo-checker/fifo_bind.sv
LINT_TOP      := fifo
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: covered is a trace and every engine finds it
include ../../common.mk
