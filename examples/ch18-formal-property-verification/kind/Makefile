# k-induction in a page, on the solver of the logic-and-solvers
# chapter: the step case fails from an unreachable state at every k
# tried and succeeds at k = 7 once repeated states are forbidden.
# Python only; about a second.
EXAMPLE_LANG  := python
TOP           := run_kind.py
SOURCES       := run_kind.py kind.py ../common/ts.py
EXPECT_OUTPUT := proven at k = 7, 16 queries
include ../../common.mk
