# history-prophecy.tcl -- A: a bounded look into the past, on the
# correct grant unit; B: the history variable, correct unit and
# mutant; C: the k-th word through the FIFO by a history variable;
# D: the same by a prophecy, asserted where it is guessed; E: the
# prophecy asserted where it is checked.
set here [file dirname [info script]]
source $here/../common.tcl
set f $here/hp.sv
puts "=== A: three cycles of \$past in place of a history variable"
design $f hist_top
assert -name a_past3 {gnt |-> $past(req) || $past(req,2) || $past(req,3)}
one informal-bmc 30s -all
expect cex a_past3
puts "=== B: the history variable"
foreach bug {0 1} {
  design $f hist_top -parameter BUG $bug
  assert -name a_seen {gnt |-> seen}
  cover  -name c_late {gnt && !$past(req) && !$past(req,2) && !$past(req,3)}
  one informal-kind 30s -all
}
set ff [list $::rtl09/fifo_fixed.sv $f]
puts "=== C: k-th word out equals k-th word in, history variable"
design $ff proph_top
assume -name m_k {$stable(k)}
assert -name a_hist {pop_k |-> rd_data == hv}
cover  -name c_popk {pop_k && k == 4'd9}
one informal-kind 30s -all
one ric3-ic3 60s -property [full a_hist]
puts "=== D: prophecy checked at the pop, asserted at the push"
design $ff proph_top
assume -name m_k  {$stable(k)}
assume -name m_pv {$stable(pv)}
assume -name m_check {pop_k |-> rd_data == pv}
assert -name a_proph {push_k |-> wr_data == pv}
one informal-bmc 30s -all
puts "=== E: the same prophecy, asserted at the pop"
design $ff proph_top
assume -name m_k  {$stable(k)}
assume -name m_pv {$stable(pv)}
assume -name m_check {pop_k |-> rd_data == pv}
assert -name a_proph_late {pop_k |-> hv == pv}
cover  -name c_popk {pop_k && k == 4'd9}
one informal-kind 30s -all
one ric3-ic3 60s -property [full a_proph_late]
finish
