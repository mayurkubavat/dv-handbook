# The one table of seconds in the chapter, generated and dated: a bug
# at four depths and the pointer property at five sizes, one engine a
# run, ten seconds allowed. What the run prints holds the verdicts
# only. `MEASURE=1 make run` also rewrites tbl-seconds.md with the
# seconds (kept under version control, so `make clean` leaves it; it
# differs from run to run by design, so an ordinary run leaves it).
# Selects ric3-ic3, so it is skipped where rIC3 is not installed.
# About forty seconds, thirty of them three limits.
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := seconds.py
SOURCES       := seconds.py ../common/tables.py
EXPECT_OUTPUT := verdict: every run ended as the chapter states
include ../../common.mk
