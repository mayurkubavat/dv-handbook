# Mutation of the design: the chapter's FIFO property set (Chapter 9's
# checker, the pointer property, the tracked-word check) against
# three one-line mutants of the repaired FIFO, each killed by named
# properties at stated depths. In-house engines only. About forty
# seconds, most of them the limits of the properties a mutant leaves
# alive.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := informal
REQUIRES      := informal
TOP           := mutants.tcl
SOURCES       := mutants.tcl ../common/ch19.tcl ../track-word/track.sv \
                 $(C09)/rtl/fifo_fixed.sv
LINT_TOP      := track
LINT_FLAGS    := -Wall -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL \
                 -Wno-SYNCASYNCNET
EXPECT_OUTPUT := verdict: every mutant killed
include ../../common.mk
