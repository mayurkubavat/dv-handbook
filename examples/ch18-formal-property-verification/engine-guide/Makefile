# The engine-selection table, generated: eight situations under three
# in-house engines and rIC3, four seconds each, written as
# tbl-engines.md (kept under version control like a run.out, so
# `make clean` leaves it). Selects ric3-ic3, so it is skipped where
# rIC3 is not installed. About forty seconds, 36 of them nine limits.
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := guide.py
SOURCES       := guide.py ../common/tables.py
EXPECT_OUTPUT := wrote tbl-engines.md
include ../../common.mk
