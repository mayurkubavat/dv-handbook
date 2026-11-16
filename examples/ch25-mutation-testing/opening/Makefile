# The chapter's first table: line, branch, expression and toggle coverage
# of the repaired FIFO under the book's four testbenches, each built
# with --coverage and read by path, beside the number of the 44 source
# mutants each kills (the source schema). Verilator only; about thirty
# seconds.
EXAMPLE_LANG  := python
TOP           := opening.py
SOURCES       := opening.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: equal code coverage, kills from 0 to 35 of 44
include ../../common.mk
