# The chapter's three solvers against z3 on small random formulas,
# random 3-SAT near its hardest ratio and the chapter's own families,
# with models and a sample of learned clauses checked. About 13 s.
# Needs the z3 Python package; without it the script prints a line
# beginning "skipped" and the checker records a skip.
EXAMPLE_LANG  := python
TOP           := selftest.py
SOURCES       := selftest.py ../dpll/dpll.py ../cdcl/cdcl.py \
                 ../cdcl/cdcl_vsids.py ../common/gen.py
EXPECT_OUTPUT := agree with z3 on every one
include ../../common.mk
