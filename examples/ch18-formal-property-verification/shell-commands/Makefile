# The table of shell commands, generated: every line of commands.list
# run in one session, and what the tool did with it written as
# tbl-shell.md (kept under version control like a run.out, so
# `make clean` leaves it). Needs informal. About three seconds.
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := commands.py
SOURCES       := commands.py ../common/tables.py
LINT_CMD      := python3 -m py_compile $(SOURCES) \
                 && echo "lint: no warnings"
EXPECT_OUTPUT := wrote tbl-shell.md
include ../../common.mk
