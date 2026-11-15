# Bounded model checking in a page: two AIGER models unrolled into one
# CNF per bound and solved by the chapter's cdcl.py. The counter fails
# at bound 6 and the first chapter's FIFO at bound 16. Python only.
EXAMPLE_LANG  := python
TOP           := run_unroll.py
SOURCES       := run_unroll.py bmc_aag.py ../common/aiger.py \
                 ../cdcl/cdcl.py
EXPECT_OUTPUT := frame 16: count is 15, so full is high
include ../../common.mk
