# What the tool shows of an engine's work: four report rows, the
# statistics line of its IC3 with the line of the certificate check,
# and the last bound its induction engine reports as a child process;
# see view.sh. About five seconds, three of them one limit.
C09           := ../../ch09-temporal-properties
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := view.sh
SOURCES       := view.sh
PYTHON        := bash
LINT_CMD      := verilator --lint-only -Wall -Wno-DECLFILENAME \
                     -Wno-UNUSEDSIGNAL -Wno-SYNCASYNCNET --top-module fifo \
                     $(C09)/rtl/fifo_fixed.sv && bash -n view.sh \
                     && echo "lint: no warnings"
EXPECT_OUTPUT := verdict: a count of frames and lemmas
include ../../common.mk
