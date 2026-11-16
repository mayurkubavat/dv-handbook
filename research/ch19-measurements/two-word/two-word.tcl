# two-word.tcl -- order, duplication and invention checked with two
# symbolic words. A: the flag form (in, out flags only), DEPTH 4;
# B: the position form (words ahead of each tracked word), DEPTH 4
# and 16; C: the flag properties with the position properties
# assumed; D: the duplicating mutant.
set here [file dirname [info script]]
source $here/../common.tcl
proc env {} {
  assume -name m_d    {$stable(d1) && $stable(d2) && d1 != d2}
  assume -name m_one1 {push1 |-> !in1}
  assume -name m_one2 {push2 |-> in1 && !in2}
}
proc flags {} {
  assert -name a_order {pop2 |-> out1}
  assert -name a_once1 {pop1 |-> in1 && !out1}
  assert -name a_once2 {pop2 |-> in2 && !out2}
  cover  -name c_both  {pop2 && out1}
}
set P1 {in1 && !out1 && a1 == '0 |-> rd_data == d1}
set P2 {in2 && !out2 && a2 == '0 |-> rd_data == d2}
set PO {in1 && !out1 && in2 && !out2 |-> a1 < a2}
proc pos {} {
  assert -name p_head1 $::P1
  assert -name p_head2 $::P2
  assert -name p_ahead $::PO
}
set ok  [list $::rtl09/fifo_fixed.sv $here/two_word.sv]
set bad [list $here/fifo_dup.sv $here/two_word.sv]

puts "=== A: flag form, DEPTH 4"
design $ok two_word -parameter DEPTH 4
env; flags
one ric3-ic3 30s -all
puts "=== B: position form"
foreach d {4 16} {
  foreach e {informal-kind ric3-ic3} {
    design $ok two_word -parameter DEPTH $d
    env; pos
    cover -name c_both {pop2 && out1}
    one $e 60s -all
  }
}
puts "=== C: flag form with the position properties assumed, DEPTH 4"
design $ok two_word -parameter DEPTH 4
env; flags
assume -name m_head1 $P1
assume -name m_head2 $P2
assume -name m_ahead $PO
one informal-kind 60s -all
one ric3-ic3 60s -all
puts "=== D: the mutant that reads a word twice"
foreach d {4 16} {
  design $bad two_word -parameter DEPTH $d
  env; flags; pos
  one informal-bmc 30s -all
}
finish
