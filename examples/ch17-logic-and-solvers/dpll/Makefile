# DPLL in a page: the full adder's question answered by unit
# propagation alone, and the adder miter, on which the search makes
# exactly 4^N - 1 decisions for N = 2 to 7. About five seconds.
EXAMPLE_LANG  := python
TOP           := run_dpll.py
SOURCES       := run_dpll.py dpll.py ../common/dimacs.py \
                 ../common/tseitin.py ../common/gen.py
EXPECT_OUTPUT := decisions = 4^N - 1 in every row
include ../../common.mk
