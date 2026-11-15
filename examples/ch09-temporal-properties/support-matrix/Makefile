# The two support matrices, regenerated from the probes on every run;
# several minutes, most of it compiling the simulators' output. Every
# column is needed: verilator, iverilog and the next Verilator release
# (VERILATOR_NEXT, default /opt/verilator-5.054/bin/verilator) must be
# there as well as informal. When one is missing, matrix.py prints a
# line beginning "skipped" and leaves matrix.md alone, and the checker
# records a skip. matrix.md is kept under version control,
# like run.out, so `make clean` leaves it.
EXAMPLE_LANG := python
TOP          := matrix.py
SOURCES      := matrix.py
REQUIRES     := informal
include ../../common.mk
