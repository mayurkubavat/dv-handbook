# The chapter's instances under z3 and CaDiCaL, written as the tables
# the chapter includes (tbl-*.md, kept under version control like a
# run.out, so `make clean` leaves them). CaDiCaL is not part of the
# book's toolchain: the checker skips this run wherever `cadical` is
# not on the PATH. Several minutes when it runs.
EXAMPLE_LANG  := python
REQUIRES      := cadical
TOP           := measure.py
SOURCES       := measure.py ../common/gen.py ../common/dimacs.py
EXPECT_OUTPUT := wrote tbl-word.md
include ../../common.mk
