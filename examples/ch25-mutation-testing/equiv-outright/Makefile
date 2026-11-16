# Two mutants equivalent outright, m32 and m36: no difference found by
# bounded search, and the miter proved by rIC3. Selects ric3-ic3, so it
# is skipped where rIC3 is not installed. About twenty-five seconds.
EXAMPLE_LANG  := python
REQUIRES      := ric3
TOP           := outright.py
SOURCES       := outright.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := verdict: m32 and m36 are equivalent outright
include ../../common.mk
