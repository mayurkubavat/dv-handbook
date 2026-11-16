# What N clean seeds prove: zero-failure bounds and their coverage in
# Python, then the coverage chapter's FIFO testbench under 250 seeds of
# a 30-cycle generator, whose clean seeds bound a probability the exact
# chain puts far lower. Writes counts.tsv (kept under version control;
# the unseen-bin example reads it). Verilator only; about 25 seconds.
EXAMPLE_LANG  := python
TOP           := run_clean.sh
SOURCES       := run_clean.sh clean.py
PYTHON        := bash
LINT_CMD      := bash -n run_clean.sh && python3 -I -B -m py_compile \
                     clean.py && echo "lint: no errors"
EXPECT_OUTPUT := verdict: 250 of 250 seeds clean
include ../../common.mk
