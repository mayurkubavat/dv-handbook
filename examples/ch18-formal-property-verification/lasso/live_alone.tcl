# live_alone.tcl -- one liveness property, refuted: "a request taken
# while idle is eventually granted". The counterexample is a path
# that ends in a loop, and the trace file says where the loop closes.
set here [file dirname [info script]]
source $here/../common/proof.tcl
puts "=== one liveness property alone"
analyze -sv12 $here/live_small.sv
elaborate -top live_small
clock clk
reset -expression {rst}
assert -name a_live {req && n == 2'd0 |-> s_eventually gnt}
one informal-bmc 20s -all
expect cex a_live
expect_depth 4 a_live

puts "--- the comment at the head of the trace file"
set f [open [trace a_live]]
while {[gets $f line] >= 0} {
  if {[string match {$comment*} $line]} {
    puts [string trim [string map {$comment "" $end ""} $line]]
  }
}
close $f
puts "--- the trace, one row per cycle"
puts [exec python3 $ch09/common/vcdtable.py [trace a_live] \
    rst req stall n gnt]

puts "=== the same property with a bounded one beside it"
assert -name a_bound4 {req && n == 2'd0 |-> ##[1:4] gnt}
one informal-bmc 20s -all
expect cex a_live a_bound4
expect_depth 7 a_live
expect_depth 5 a_bound4
puts "--- the comment at the head of the trace file of a_live"
set f [open [trace a_live]]
gets $f line
close $f
puts [string trim [string map {$comment "" $end ""} $line]]
puts "verdict: a stem of three cycles and a loop of one, held by\
 stall; a second property in the session lengthens what is printed"
finish
