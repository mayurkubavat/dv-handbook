# The chapter's five small models, regenerated from fifo_ptrs.sv with
# InFormal and compared byte for byte with the AIGER files the Python
# examples read. Needs informal; the checker skips the run without it.
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := run_models.py
SOURCES       := run_models.py
LINT_CMD      := verilator --lint-only -Wall -Wno-DECLFILENAME \
                 -Wno-UNUSEDSIGNAL -Wno-PROCASSINIT -Wno-SYNCASYNCNET \
                 --top-module fifo_ptrs \
                 ../../ch09-temporal-properties/rtl/fifo_fixed.sv \
                 ../common/fifo_ptrs.sv \
                 && python3 -m py_compile $(SOURCES)
EXPECT_OUTPUT := regenerated models equal the checked-in files
include ../../common.mk
