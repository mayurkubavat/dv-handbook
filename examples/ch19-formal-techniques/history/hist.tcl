# hist.tcl -- history and prophecy variables, in-house engines.
# A: three cycles of $past in place of a history variable, on the
# correct grant unit; B: the history variable, on the correct unit
# and on the mutant; C: the k-th word out of the book's FIFO: the
# witness cover of its pop, and a prophecy of it, checked by an
# assumption at the k-th pop and asserted at the k-th push.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f $here/hp.sv

puts "=== A: three cycles of \$past in place of a history variable"
design $f hist_top
assert -name a_past3 {gnt |-> $past(req) || $past(req,2) || $past(req,3)}
one informal-bmc 5s -all
expect cex     a_past3
expect_depth 5 a_past3

puts "=== B: the history variable"
foreach bug {0 1} {
  puts "--- BUG = $bug"
  design $f hist_top -parameter BUG $bug
  assert -name a_seen {gnt |-> seen}
  cover  -name c_late \
      {gnt && !$past(req) && !$past(req,2) && !$past(req,3)}
  one informal-kind 5s -all
  expect [expr {$bug ? "cex" : "proven"}] a_seen
  expect covered c_late
}

puts "=== C: the k-th word: its witness cover, and a prophecy asserted\
 where it is guessed"
# A run with covers only: the tool prints that the design has no
# assertions, which is true of this session and harmless.
puts "--- the pop numbered k = 9 happens (the proofs are in history-ric3/)"
design [list $rtl09/fifo_fixed.sv $f] proph_top
assume -name m_k    {$stable(k)}
cover  -name c_popk {pop_k && k == 4'd9}
one informal-kind 5s -all
expect covered  c_popk
expect_depth 11 c_popk
puts "--- the prophecy"
design [list $rtl09/fifo_fixed.sv $f] proph_top
assume -name m_k     {$stable(k)}
assume -name m_pv    {$stable(pv)}
assume -name m_check {pop_k |-> rd_data == pv}
assert -name a_proph {push_k |-> wr_data == pv}
one informal-bmc 5s -all
expect cex     a_proph
expect_depth 1 a_proph
puts [exec python3 $ex/ch09-temporal-properties/common/vcdtable.py \
    [trace a_proph] rst_n wr_en push_k pop_k]
puts "verdict: the history bit proves what three cycles of \$past\
 cannot; the prophecy fails at depth 1 on a correct FIFO"
finish
