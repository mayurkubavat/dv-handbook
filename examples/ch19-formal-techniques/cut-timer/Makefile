# Black box, cut point and timer abstraction on the previous chapter's
# handshake, read by path: what each keeps, the spurious trace each
# allows, the gap assumption that removes it and its proof on the
# real timer, and an assumption whose window ends too late. About
# thirty seconds.
C18           := ../../ch18-formal-property-verification
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := cut.tcl
SOURCES       := cut.tcl ../common/ch19.tcl $(C18)/common/proof.tcl \
                 $(C18)/over-constraint/handshake.sv timer_chk.sv
LINT_TOP      := handshake
EXPECT_OUTPUT := verdict: each cut keeps the proofs
include ../../common.mk
