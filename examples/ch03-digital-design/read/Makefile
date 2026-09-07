# Chapter 3: read the two-clock design with the book's tools.
#   make run     domains, crossings, unreset registers, block diagram
# Exits non-zero because the design has an unsynchronized crossing, which
# is the point of the example.
EXAMPLE_LANG := python
TOP          := read_design.py
SOURCES      := read_design.py
EXPECT       := fail   # the tool finds the missing synchronizer
EXPECT_OUTPUT := unsynchronized: 2
include ../../common.mk
