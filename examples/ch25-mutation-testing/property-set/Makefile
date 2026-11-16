# The formal property set as a judge of the 44 source mutants: each by
# bounded search, 2 s for each property in a fixed order, stopping at
# the first counterexample; refusals by the front end counted apart; the
# first kills checked against the full per-property run in the committed
# measure.out. `MEASURE=1 make run` rewrites measure.out (several
# minutes). In-house engines only; about a minute.
EXAMPLE_LANG  := python
REQUIRES      := informal
TOP           := props.py
SOURCES       := props.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: the property set kills every non-equivalent mutant
include ../../common.mk
