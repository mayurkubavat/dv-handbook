# Chapter 4: one race, two simulators.
#
# This example is a comparison, so it drives both simulators itself rather
# than taking SIM from the environment. `make run` prints each simulator's
# answer for the racing design and for the race-free one, with a verdict
# line for each pair.
#
# EXPECT_OUTPUT pins the disagreement: if a simulator is missing the run
# fails, and without this marker that failure would be recorded as the
# finding the example exists to produce.
EXAMPLE_LANG  := python
TOP           := run_both.sh
SOURCES       := racy.sv safe.sv tb_race.sv
PYTHON        := bash
EXPECT_OUTPUT := verdict: the two simulators disagree on racy
# The testbench uses delays and event controls, so a lint of it has to say
# how those are handled; --timing is the same choice `run` makes.
# Lint says something useful here, so the recipe shows both halves: the
# race-free design passes -Wall in silence, and the racing one earns the
# warning about blocking assignments in a sequential process.
LINT_CMD := ./lint_both.sh
include ../../common.mk

clean::
	rm -rf build
