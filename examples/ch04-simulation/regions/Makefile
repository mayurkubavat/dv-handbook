# Chapter 4: the scheduling regions, observed rather than asserted.
#
# Four-state, event-driven: this example is about ordering a statically
# scheduled tool does not reproduce, so it runs on Icarus only.
EXAMPLE_LANG  := python
TOP           := run.sh
SOURCES       := tb_regions.sv
PYTHON        := bash
# BLKSEQ is waived here and nowhere else in this chapter: the blocking
# assignment in a clocked block is the thing being demonstrated, and the
# race example next door shows lint catching the same construct when it is
# a mistake rather than an illustration.
LINT_CMD      := verilator --lint-only -Wall --timing --timescale 1ns/1ps \
                     -Wno-DECLFILENAME -Wno-BLKSEQ --top-module tb_regions \
                     tb_regions.sv \
                     && echo "lint: no warnings (BLKSEQ waived, see Makefile)"
EXPECT_OUTPUT := $strobe sees b=1
include ../../common.mk

clean::
	rm -rf build
