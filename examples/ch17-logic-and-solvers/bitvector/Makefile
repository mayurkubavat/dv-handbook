# One theorem about multiplication asked three ways of z3, and four
# facts about bit-vector arithmetic that differ from a first guess.
# Needs the z3 Python package; without it the script prints a line
# beginning "skipped".
EXAMPLE_LANG  := python
TOP           := word_vs_bits.py
SOURCES       := word_vs_bits.py ../common/gen.py ../common/tseitin.py
EXPECT_OUTPUT := simplify(a*b != b*a) = False
include ../../common.mk
