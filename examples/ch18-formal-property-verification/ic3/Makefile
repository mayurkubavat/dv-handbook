# IC3 in a page: every event of its run on the two-entry FIFO, the six
# lemmas it ends with, and the check that they allow exactly the 22
# reachable states. Python only; about three seconds.
EXAMPLE_LANG  := python
TOP           := run_ic3.py
SOURCES       := run_ic3.py ic3.py ../common/ts.py
EXPECT_OUTPUT := verdict: the invariant IC3 built allows exactly
include ../../common.mk
