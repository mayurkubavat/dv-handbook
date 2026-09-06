# UVM "hello" test for the counter (see the build appendix).
# Runs on Questa/VCS/Xcelium with their bundled UVM. With Verilator,
# set UVM_HOME to a UVM source tree to lint; running needs a commercial
# simulator.
EXAMPLE_LANG := sv
TOP          := tb_top
SOURCES      := ../rtl/counter.sv counter_if.sv counter_pkg.sv tb_top.sv
UVM          := 1
UVM_TEST     := counter_smoke_test
REQUIRES     := commercial
include ../../common.mk
