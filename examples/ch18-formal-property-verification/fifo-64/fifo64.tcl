# fifo64.tcl -- the pointer property on a FIFO of 64 entries, as a
# procedure: covers, a bounded search, the engines alone, the helper,
# the proof with the helper assumed, and the covers again.
set here [file dirname [info script]]
source $here/../common/proof.tcl
analyze -sv12 $ch09/rtl/fifo_fixed.sv
elaborate -top fifo -parameter DEPTH 64 -parameter WIDTH 1
clock clk
reset -expression {!rst_n}
assert -name EmptyPtrs_A {empty |-> wr_ptr == rd_ptr}
# The helper, typed once: asserted here, assumed in step 6.
set helper {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
assert -name CountPtrs_A $helper
# Witnesses: the FIFO fills; it is empty again after a write, which is
# the antecedent of EmptyPtrs_A in a state other than reset's; and it
# drains, full to empty in 64 reads.
cover -name Full_C       {full}
cover -name EmptyAgain_C {empty && wr_ptr != '0}
cover -name Drain_C      {full ##64 empty}
set covers {Full_C EmptyAgain_C Drain_C}
set summary {}

# note STEP NAME ... -- lines of the summary printed last, naming the
# engine and the limit of the last `one`.
proc note {step args} {
  foreach name $args {
    set d [depth $name]
    lappend ::summary [format "  %-4s %-13s %-4s %-13s %s" $step \
        $::one_engine $::one_limit $name \
        "[get_status $name][expr {$d < 0 ? "" : ", depth $d"}]"]
  }
}

puts "=== step 1: the covers, by bounded search"
assert -disable EmptyPtrs_A CountPtrs_A
one informal-bmc 20s -all
expect covered {*}$covers
expect_depth 65  Full_C
expect_depth 3   EmptyAgain_C
expect_depth 129 Drain_C
note 1 {*}$covers
cover -disable {*}$covers

puts "=== step 2: a bounded search for a counterexample"
assert -enable EmptyPtrs_A
one informal-bmc 3s -all
expect undetermined EmptyPtrs_A
note 2 EmptyPtrs_A

puts "=== step 3: induction"
one informal-kind 5s -all
expect undetermined EmptyPtrs_A
note 3 EmptyPtrs_A

puts "=== step 4: IC3, in-house and external"
one informal-ic3 5s -all
expect undetermined EmptyPtrs_A
note 4 EmptyPtrs_A
one ric3-ic3 20s -all
expect proven EmptyPtrs_A
note 4 EmptyPtrs_A

puts "=== step 5: the helper alone, by induction"
assert -disable EmptyPtrs_A
assert -enable  CountPtrs_A
one informal-kind 5s -all
expect proven CountPtrs_A
note 5 CountPtrs_A

puts "=== step 6: the property with the helper assumed"
assert -disable CountPtrs_A
assert -enable  EmptyPtrs_A
assume -name CountPtrs_M $helper
one informal-kind 5s -all
expect proven EmptyPtrs_A
note 6 EmptyPtrs_A
one informal-ic3 5s -all
expect proven EmptyPtrs_A
note 6 EmptyPtrs_A

puts "=== step 7: the covers again, under the assumption"
assert -disable EmptyPtrs_A
cover -enable {*}$covers
one informal-bmc 20s -all
expect covered {*}$covers
expect_depth 65  Full_C
expect_depth 3   EmptyAgain_C
expect_depth 129 Drain_C
note 7 {*}$covers
puts "=== summary: step, engine, limit, property, answer"
puts [join $summary "\n"]
puts "verdict: proven with one helper, itself proven; three witness\
 covers reached with and without it"
finish
