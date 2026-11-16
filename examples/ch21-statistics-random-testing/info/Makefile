# Information measures of stimulus: the constrained-random chapter's
# laws as effective numbers of values, G against Pearson's statistic on
# its printed counts (read by path), the bias of plug-in entropy, and
# the coverage chapter's FIFO testbench under eight generators made of
# its two knobs, with mutual information ranking which knob moves which
# bin. Writes tbl-ch21-knob.md (kept under version control). Verilator
# only; about 40 seconds.
EXAMPLE_LANG  := python
TOP           := run_info.sh
SOURCES       := run_info.sh info.py
PYTHON        := bash
LINT_CMD      := bash -n run_info.sh && python3 -I -B -m py_compile \
                     info.py && echo "lint: no errors"
EXPECT_OUTPUT := verdict: entropy peaks at even 400, bins per seed at push 400
include ../../common.mk
