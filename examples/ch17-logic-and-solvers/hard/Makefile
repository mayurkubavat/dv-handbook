# Where the chapter's solvers struggle: pigeonhole formulas, the
# multiplier miter beside the adder miter, and random 3-SAT across
# the clause-to-variable ratio. About twelve seconds.
EXAMPLE_LANG  := python
TOP           := run_hard.py
SOURCES       := run_hard.py ../dpll/dpll.py ../cdcl/cdcl.py \
                 ../cdcl/cdcl_vsids.py ../common/gen.py
EXPECT_OUTPUT := the median cost peaks where about half
include ../../common.mk
