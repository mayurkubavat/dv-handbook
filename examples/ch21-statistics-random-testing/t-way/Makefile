# t-way combinatorial coverage: optimal binary and orthogonal-array
# constructions, a greedy array on the architecture chapter's DMA
# transfer space with its exclusions as constraints, random selection
# of the same space under three generators, and that chapter's own
# random test (its testbench and RTL read by path) against the model of
# its generator. Writes data.tsv (kept under version control). Verilator
# 5.052; about 35 seconds.
EXAMPLE_LANG  := python
TOP           := run_tway.sh
SOURCES       := run_tway.sh tway.py
PYTHON        := bash
LINT_CMD      := bash -n run_tway.sh && python3 -I -B -m py_compile \
                     tway.py && echo "lint: no errors"
EXPECT_OUTPUT := verdict: greedy 23 rows for every legal pair, 68 for every
include ../../common.mk
