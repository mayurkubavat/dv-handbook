# Version 2's plan, reported by Chapter 2's tool from the examples' status.
# Two items have no test yet, one of them a must-have, so the report
# exits non-zero: the plan is not closed, and saying so is its job.
EXAMPLE_LANG  := python
TOP           := ../../ch02-verification-planning/plan/plan_report.py
SOURCES       := ../../ch02-verification-planning/plan/plan_report.py
PLUSARGS      := --plan dma_plan.yaml --status ../../status.json
EXPECT        := fail
EXPECT_OUTPUT := must-have items without a passing test: DMA-009
include ../../common.mk
