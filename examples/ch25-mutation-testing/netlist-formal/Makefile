# The formal half of the netlist population: a uniform sample of 100
# mutations (seed 25), each judged by the property set and by a miter.
# `MEASURE=1 make run` runs the sample into measure.out (several
# minutes); the default run recomputes its summary with intervals and
# reruns two equivalents and the two deepest differences by rIC3, and
# a_integrity alone on each of the fourteen misses with more time.
# Selects ric3-ic3, so it is skipped where rIC3 is not installed. About
# a minute and a half.
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := nformal.py
SOURCES       := nformal.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: the formal sample's summary is reproduced
include ../../common.mk
