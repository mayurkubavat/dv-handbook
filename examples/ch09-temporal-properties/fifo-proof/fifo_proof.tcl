# fifo_proof.tcl -- the repaired FIFO: the checker's properties proved,
# then one property of the design's own registers that an induction
# engine cannot settle alone.
set here [file dirname [info script]]
set rtl  $here/../rtl/fifo_fixed.sv
set_prove_time_limit 60s

puts "=== the checker, bound to the repaired FIFO"
analyze -sv12 $rtl $here/../fifo-checker/fifo_sva.sv \
    $here/../fifo-checker/fifo_bind.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}
informal::set_engines informal-kind
prove -all
expect proven  NoOverflow_A FullForward_A FullBackward_A EmptyExact_A \
               PushFull_A PopEmpty_A Sync_A
expect covered FullReached_C PushFull_C PopEmpty_C Drained_C

# The second half names registers inside the design, as Tcl properties.
clear -all
analyze -sv12 $rtl
elaborate -top fifo
clock clk
reset -expression {!rst_n}
set_prove_time_limit 10s
assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
assert -name CountPtrs_A {count[3:0] == wr_ptr - rd_ptr}

puts "=== bounded model checking alone: a search for counterexamples"
informal::set_engines informal-bmc
prove -all
expect undetermined EmptyPtrs_A CountPtrs_A

puts "=== k-induction, each property alone"
informal::set_engines informal-kind
prove -all
expect undetermined EmptyPtrs_A
expect proven       CountPtrs_A

puts "=== k-induction, with the property it just proved assumed"
assert -disable CountPtrs_A
assume -name CountPtrs_M {count[3:0] == wr_ptr - rd_ptr}
prove -all
expect proven EmptyPtrs_A

puts "=== IC3, no helper"
assume -remove CountPtrs_M
informal::set_engines informal-ic3
prove -all
expect proven EmptyPtrs_A
puts "verdict: true, and out of reach of induction until a helper\
 invariant is assumed"
finish
