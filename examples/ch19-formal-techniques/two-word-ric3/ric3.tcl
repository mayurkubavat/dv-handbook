# ric3.tcl -- the two-word check of two-word/ handed to rIC3 with no
# helper, DEPTH 4: the flag form, then the position form.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set files [list $rtl09/fifo_fixed.sv $here/../two-word/two_word.sv]
proc words {} {
  design $::files two_word -parameter DEPTH 4
  assume -name m_d    {$stable(d1) && $stable(d2) && d1 != d2}
  assume -name m_one1 {push1 |-> !in1}
  assume -name m_one2 {push2 |-> in1 && !in2}
}

puts "=== A: the flag form"
words
assert -name a_order {pop2 |-> out1}
assert -name a_once1 {pop1 |-> in1 && !out1}
assert -name a_once2 {pop2 |-> in2 && !out2}
cover  -name c_both  {pop2 && out1}
one ric3-ic3 5s -all
expect undetermined a_order a_once1 a_once2
expect covered      c_both

puts "=== B: the position form"
words
assert -name p_head1 {in1 && !out1 && a1 == '0 |-> rd_data == d1}
assert -name p_head2 {in2 && !out2 && a2 == '0 |-> rd_data == d2}
assert -name p_ahead {in1 && !out1 && in2 && !out2 |-> a1 < a2}
one ric3-ic3 10s -all
expect proven       p_head1 p_head2
expect undetermined p_ahead
puts "verdict: without the slot helpers rIC3 proves neither ordering\
 property"
finish
