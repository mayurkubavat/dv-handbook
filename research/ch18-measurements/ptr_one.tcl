# ptr_one.tcl -- one property, one engine: used by certify.sh.
source [file dirname [info script]]/common.tcl
analyze -sv12 $ch09/rtl/fifo_fixed.sv
elaborate -top fifo -parameter DEPTH $::env(DEPTH) -parameter WIDTH 1
clock clk
reset -expression {!rst_n}
set_prove_time_limit 20s
assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
informal::set_engines informal-ic3
prove -all
