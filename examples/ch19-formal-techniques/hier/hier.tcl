# hier.tcl -- a pipe of two FIFOs (common/hier.sv), DEPTH 16, proved
# with each FIFO black-boxed under its contract (proved in contract/).
# P1: the pipe is empty when its count G is 0; P2: when it is full, G
# is at least DEPTH. A: the full contract assumed; B: half of it;
# C: the parent's own helper, proved, then assumed.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set files [list $rtl09/fifo_fixed.sv $here/../common/hier.sv]
set d 16
# The parent helper, typed once: G is the sum of the two ghost counts,
# each at most DEPTH.
set HP "G == 6'(u0.g) + 6'(u1.g) && u0.g <= $d && u1.g <= $d"

# boxed CONTRACT -- a new session on the pipe with both FIFOs boxed;
# CONTRACT is "full" (empty and full) or "half" (empty only).
proc boxed {contract} {
  design $::files pipe2 -parameter DEPTH $::d -bbox_m {fifo}
  foreach u {u0 u1} {
    assume -name ${u}_CE "$u.empty == ($u.g == '0)"
    if {$contract eq "full"} {
      assume -name ${u}_CF "$u.full == ($u.g == $::d)"
    }
  }
}
proc p1 {} {assert -name P1_A {G == '0 |-> empty}}
proc p2 {} {assert -name P2_A "full |-> G >= $::d"}
proc both {} {cover -name Both_C "u0.g == $::d && u1.g == $::d"}

puts "=== A: both FIFOs boxed, the contract assumed"
boxed full
p1; p2; both
one informal-kind 5s -all
expect undetermined P1_A P2_A
expect covered      Both_C
expect_depth 33     Both_C

puts "=== B: half the contract (empty only)"
boxed half
p2
one informal-kind 5s -all
expect cex     P2_A
expect_depth 1 P2_A

puts "=== C: the parent's helper"
puts "--- alone"
boxed full
assert -name HP_A $HP
one informal-kind 5s -all
expect proven HP_A
puts "--- assumed"
boxed full
assume -name HP_M $HP
p1; p2; both
one informal-kind 5s -all
expect proven   P1_A P2_A
expect covered  Both_C
expect_depth 33 Both_C
puts "verdict: the boxed pipe proven with its children's contracts and\
 one parent helper"
finish
