# Chapter 5: a reset that never happened.
#
# A comparison across both simulators, so the example drives them itself.
# EXPECT_OUTPUT pins the verdict line: a missing simulator must fail the
# run rather than be recorded as the finding.
EXAMPLE_LANG  := python
TOP           := run_both.sh
SOURCES       := dut_reg.sv tb_bit.sv tb_logic.sv tb_fixed.sv
PYTHON        := bash
EXPECT_OUTPUT := verdict: only the manufactured edge resets on both simulators
LINT_CMD      := ./lint.sh
include ../../common.mk

clean::
	rm -rf build
