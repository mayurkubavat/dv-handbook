# fifo_ptr.tcl -- "empty implies equal pointers" on the repaired FIFO:
# true, not inductive; and the helper that makes it so. Every proving
# engine alone, at DEPTH given in the environment.
source [file dirname [info script]]/common.tcl
set depth $::env(DEPTH)
clear -all
analyze -sv12 $ch09/rtl/fifo_fixed.sv
elaborate -top fifo -parameter DEPTH $depth -parameter WIDTH 1
clock clk
reset -expression {!rst_n}
assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
assert -name CountPtrs_A {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
puts "=== DEPTH=$depth"
each_engine [concat informal-bmc $provers] 20s -all
puts "=== DEPTH=$depth, the helper assumed"
assert -disable CountPtrs_A
assume -name CountPtrs_M {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
each_engine $provers 20s -all
