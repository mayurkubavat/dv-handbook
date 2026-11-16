# The coverage chapter's FIFO testbench under 1000 seeds of one
# generator, one coverage database each: per-seed and per-cycle hit
# rates, seeds to close fifo_cg, the bug trigger against the exact
# chain. Writes data.tsv, curve.tsv and counts.tsv (kept under version
# control like run.out; the unseen-bin example reads counts.tsv).
# Verilator only (covergroups); about 25 seconds.
EXAMPLE_LANG  := python
TOP           := run_seeds.sh
SOURCES       := run_seeds.sh seed_unit.py
PYTHON        := bash
LINT_CMD      := bash -n run_seeds.sh && python3 -I -B -m py_compile \
                     seed_unit.py && echo "lint: no errors"
EXPECT_OUTPUT := verdict: 247 of 1000 seeds triggered the bug
include ../../common.mk
