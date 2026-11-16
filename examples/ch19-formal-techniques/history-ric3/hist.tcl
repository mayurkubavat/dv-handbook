# hist.tcl -- the k-th word out of the book's FIFO against the k-th
# word in, DEPTH 4, by rIC3. A: by a history variable that records
# the k-th pushed word; B: by a prophecy, asserted only where the
# assumption that checks it has run. Each proof has the witness cover
# of the k-th pop beside it, as in history/.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set files [list $rtl09/fifo_fixed.sv $here/../history/hp.sv]

puts "=== A: a history variable"
design $files proph_top
assume -name m_k    {$stable(k)}
assert -name a_hist {pop_k |-> rd_data == hv}
cover  -name c_popk {pop_k && k == 4'd9}
one ric3-ic3 30s -all
expect proven  a_hist
expect covered c_popk

puts "=== B: a prophecy, asserted at the pop"
design $files proph_top
assume -name m_k     {$stable(k)}
assume -name m_pv    {$stable(pv)}
assume -name m_check {pop_k |-> rd_data == pv}
assert -name a_proph_late {pop_k |-> hv == pv}
cover  -name c_popk {pop_k && k == 4'd9}
one ric3-ic3 30s -all
expect proven  a_proph_late
expect covered c_popk
puts "verdict: the k-th word proven by history, and by a prophecy read\
 only at the pop"
finish
