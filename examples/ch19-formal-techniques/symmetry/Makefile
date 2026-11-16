# Symmetry on a four-port arbiter: with a free initial `last` one
# port is proved and a rotation check shows the ports interchangeable;
# with `last` reset to 3, as the DMA resets its pointer, the rotation
# fails at reset and each port is proved on its own; fixed priority
# is not symmetric at all; the DMA's two channels are proved one by
# one. A few seconds.
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := sym.tcl
SOURCES       := sym.tcl ../common/ch19.tcl rr_arb.sv
LINT_TOP      := rr_rot
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: a symmetry argument holds for the free start
include ../../common.mk
