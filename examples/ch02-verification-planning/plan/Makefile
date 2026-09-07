# Chapter 2: the FIFO's verification plan and the report tool that reads it.
#   make run                     report against examples/status.json
#   make run PLUSARGS=--verbose  show every item's evidence
EXAMPLE_LANG := python
TOP          := plan_report.py
SOURCES      := plan_report.py
EXPECT       := fail   # the report exits non-zero: the FIFO is not done
include ../../common.mk
