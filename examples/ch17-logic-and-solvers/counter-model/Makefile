# A 3-bit counter lowered to a word-level model (Btor2, 20 lines) and
# a bit-level one (AIGER), and refuted at depth 6 by bounded model
# checking. Needs informal; the checker skips the run without it.
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := run_model.py
SOURCES       := run_model.py ../common/informal_model.py
LINT_CMD      := verilator --lint-only -Wall -Wno-DECLFILENAME \
                 -Wno-PROCASSINIT --top-module counter counter.sv \
                 && python3 -m py_compile $(SOURCES)
EXPECT_OUTPUT := verdict: the counter reaches 6
include ../../common.mk
