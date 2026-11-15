# Lint both versions with the book's flags. Version 1 is kept as found,
# so its warnings are the output, not a failure; version 2 must be clean.
EXAMPLE_LANG  := python
TOP           := run_lint.sh
SOURCES       := run_lint.sh
PYTHON        := bash
LINT_CMD      := bash -n run_lint.sh
EXPECT_OUTPUT := verdict: version 1 has 2 registers
include ../../common.mk
