# The chapter's shared Python: statlib.py (statistics on the standard
# library alone), fifo_chain.py (an exact Markov chain of the FIFO) and
# dat.py (covergroup bins from Verilator .dat files). make run runs the
# self-test against values known in closed form. Under a second.
EXAMPLE_LANG  := python
TOP           := selftest.py
SOURCES       := selftest.py statlib.py fifo_chain.py dat.py
PYTHON        := python3 -I -B
EXPECT_OUTPUT := self-test: the library reproduces every tabulated value
include ../../common.mk
