# How many bins will this generator ever reach? Good-Turing, Chao1 and
# Chao2 on a synthetic space with a known truth, then on fifo_cg under
# two generators, from the seed-by-bin tables seed-unit/ and
# clean-seeds/ write (counts.tsv, read by path). Writes data.tsv (kept
# under version control). Python only; fixed Python seed; a second.
EXAMPLE_LANG  := python
TOP           := unseen.py
SOURCES       := unseen.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: 250 seeds of 30 cycles saw 22 of 28 reachable bins
include ../../common.mk
