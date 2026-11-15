# The chapter's three solvers against z3 on 3,000 random formulas.
# Needs the z3 Python package; without it the script prints a line
# beginning "skipped" and the checker records a skip.
EXAMPLE_LANG  := python
TOP           := selftest.py
SOURCES       := selftest.py ../dpll/dpll.py ../cdcl/cdcl.py \
                 ../cdcl/cdcl_vsids.py
EXPECT_OUTPUT := agree with z3 on every one
include ../../common.mk
