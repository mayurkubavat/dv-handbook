# Clause learning in under 170 lines: one conflict analyzed step by step,
# and the adder miter under three solvers that differ in one idea
# each. About ten seconds, most of it cdcl.py at 12 bits.
EXAMPLE_LANG  := python
TOP           := run_cdcl.py
SOURCES       := run_cdcl.py cdcl.py cdcl_vsids.py ../dpll/dpll.py \
                 ../common/dimacs.py ../common/tseitin.py ../common/gen.py
EXPECT_OUTPUT := with the learned clause negated: UNSATISFIABLE
include ../../common.mk
