# The self-test of the chapter's engines: ic3.py and kind.py against
# explicit-state search on 300 random systems and the 86 single-edge
# mutants of the two-entry FIFO. One wrong verdict, trace or invariant
# fails the run. Python only; about fifteen seconds.
EXAMPLE_LANG  := python
TOP           := fuzz.py
SOURCES       := fuzz.py ../ic3/ic3.py ../kind/kind.py ../common/ts.py
PLUSARGS      := 300 18
EXPECT_OUTPUT := self-test passed: no disagreement
include ../../common.mk
