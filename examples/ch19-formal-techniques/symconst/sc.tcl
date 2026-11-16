# sc.tcl -- a symbolic constant, two ways. A: $anyconst, with its RTL
# assertion; B: a free input held by $stable, with the same RTL
# assertion; C: what the $stable assumption says about the reset
# cycle.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set fifo $rtl09/fifo_fixed.sv

puts "=== A: \$anyconst"
design [list $fifo $here/sc_any.sv] sc_any
puts "properties listed: [llength [get_property_list]]"
one informal-kind 5s -all
if {[llength [get_property_list]] != 0} {
  puts "unexpected: the RTL assertion is listed"
  incr ::unexpected
}

puts "=== B: a free input, held by an assumption"
design [list $fifo $here/sc_free.sv] sc_free
assume -name m_sa {$stable(sa)}
puts "properties listed: [llength [get_property_list]]"
one informal-kind 5s -all
expect proven Slot_A

puts "=== C: the reset cycle"
# sa0 holds sa as it was in the reset cycle when first is 1.
design [list $fifo $here/sc_free.sv] sc_free
assume -name m_sa {$stable(sa)}
assert -disable *Slot_A
assert -name C0_A  {first |-> sa0 == sa}
cover  -name C0_C  {first && sa0 != sa}
cover  -name C1_C  {first}
one informal-kind 5s -all
expect proven      C0_A
expect unreachable C0_C
expect covered     C1_C
puts "verdict: the anyconst spelling leaves no RTL property; the free\
 input keeps them, and \$stable binds the reset cycle too"
finish
