# The repaired FIFO proved with InFormal, and one true property of its
# pointers that k-induction leaves undetermined until a helper
# invariant is assumed; see fifo_proof.tcl. About half a minute, most
# of it the time limit of the proof that does not finish.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := fifo_proof.tcl
SOURCES       := fifo_proof.tcl ../rtl/fifo_fixed.sv \
                 ../fifo-checker/fifo_sva.sv ../fifo-checker/fifo_bind.sv
LINT_TOP      := fifo
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: true, and out of reach of induction
include ../../common.mk
