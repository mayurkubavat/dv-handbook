# Version 2's plan, reported by the planning chapter's tool from the
# examples' status.
# Revision 1 left the maximum length (a must-have) without a test and
# the report failed on it; revision 2 adds the test. Reset during a
# transfer (a should) is still open, and the report lists it.
EXAMPLE_LANG  := python
TOP           := ../../ch02-verification-planning/plan/plan_report.py
SOURCES       := ../../ch02-verification-planning/plan/plan_report.py
PLUSARGS      := --plan dma_plan.yaml --status ../../status.json
EXPECT_OUTPUT := every must-have item has a passing test
include ../../common.mk
