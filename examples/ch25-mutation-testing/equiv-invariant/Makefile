# A mutant equivalent only on the reachable states, m43: bounded search,
# k-induction alone, the helper count <= 16, k-induction with it
# assumed, the flag half alone, and rIC3. Selects ric3-ic3, so it is
# skipped where rIC3 is not installed. About thirty seconds.
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := invariant.py
SOURCES       := invariant.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: m43 is equivalent on the reachable states
include ../../common.mk
