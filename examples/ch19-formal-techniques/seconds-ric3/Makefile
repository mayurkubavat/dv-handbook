# The chapter's one table of seconds, generated and dated: the rows
# with a verdict from mem-abs, hier, hier-ric3, case-split and
# history-ric3, one property and one engine a run, sixty seconds
# allowed. What the run prints holds the verdicts only. `MEASURE=1
# make run` also rewrites tbl-seconds.md with the seconds (kept under
# version control, so `make clean` leaves it; it differs from run to
# run by design, so an ordinary run leaves it). Selects ric3-ic3, so
# it is skipped where rIC3 is not installed. About ninety seconds.
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := seconds.py
SOURCES       := seconds.py \
                 ../../ch18-formal-property-verification/common/tables.py
EXPECT_OUTPUT := verdict: every run proven, as the chapter states
# Lint compiles the sources in memory: py_compile would write a
# __pycache__ into the other chapter's tree.
LINT_CMD       = python3 -c 'import sys; [compile(open(f).read(), f, \
                 "exec") for f in sys.argv[1:]]' $(SOURCES)
include ../../common.mk
