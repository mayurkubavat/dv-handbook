# The chapter's FIFO checker under InFormal, on the first chapter's
# FIFO: one direction of "full exactly at sixteen" refuted, the other
# proved vacuously, and the cover that says so; see fifo.tcl.
C01           := ../../ch01-what-is-dv
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := fifo.tcl
SOURCES       := fifo.tcl $(C01)/rtl/fifo.sv ../fifo-checker/fifo_sva.sv \
                 ../fifo-checker/fifo_bind.sv
LINT_TOP      := fifo
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: one direction refuted
include ../../common.mk
