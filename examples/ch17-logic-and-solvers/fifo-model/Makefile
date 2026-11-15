# The first chapter's FIFO, with reset and an occupancy counter
# written as hardware, lowered to a model: 146 state bits and 992
# ANDs, 10 latches and 102 ANDs after preprocessing, refuted at depth
# 16. Needs informal; the checker skips the run without it.
C01           := ../../ch01-what-is-dv
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := run_model.py
SOURCES       := run_model.py ../common/informal_model.py
LINT_CMD      := verilator --lint-only -Wall -Wno-DECLFILENAME \
                 -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT -Wno-SYNCASYNCNET \
                 --top-module fifo_bmc $(C01)/rtl/fifo.sv fifo_bmc.sv \
                 && python3 -m py_compile $(SOURCES)
EXPECT_OUTPUT := verdict: full is high with fewer than sixteen
include ../../common.mk
