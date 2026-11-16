# Worked example: sizing and signing off the FIFO regression. A pilot of
# the coverage chapter's testbench, the union bound from it, a fresh
# merged run of that size, unseen-bin and stimulus checks, then the
# temporal-properties chapter's checking testbench on the repaired and
# the original FIFO for the clean-seed sentence. All RTL and testbenches
# read by path. Verilator only; about 45 seconds (three builds).
EXAMPLE_LANG  := python
TOP           := run_worked.sh
SOURCES       := run_worked.sh worked.py
PYTHON        := bash
LINT_CMD      := bash -n run_worked.sh && python3 -I -B -m py_compile \
                     worked.py && echo "lint: no errors"
EXPECT_OUTPUT := verdict: 32 seeds closed fifo_cg; 1000 of 1000 clean
include ../../common.mk
