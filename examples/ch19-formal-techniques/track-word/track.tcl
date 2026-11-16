# track.tcl -- data integrity of the book's FIFO by one tracked word.
# A: the check alone, by induction and IC3, at DEPTH 16 and 4; B: a
# helper that names the one memory slot holding the tracked word,
# proved alone; C: the check with the helper assumed, and its witness
# cover; D: a mutant whose read pointer steps by two.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set fifo $rtl09/fifo_fixed.sv
set skip [mutant fifo_skip $fifo \
    {s/rd_ptr <= rd_ptr + 1'b1;/rd_ptr <= rd_ptr + 2'd2;/}]
set a_integrity {in_q && ahead == '0 |-> rd_data == sd}
# The helper, typed once: while the tracked word is inside, the slot
# `ahead` places past the read pointer holds it, and fewer than count
# words are ahead of it; and the previous chapter's pointer helper,
# with the count in range.
set helper {(!in_q || u.mem[u.rd_ptr + ahead[$clog2(DEPTH)-1:0]] == sd
              && ahead < u.count)
            && u.count[$clog2(DEPTH)-1:0] == u.wr_ptr - u.rd_ptr
            && u.count <= DEPTH}

# tracked FILE DEPTH -- a new session on the wrapper, sd held.
proc tracked {file d} {
  design [list $file $::here/track.sv] track -parameter DEPTH $d
  assume -name m_sd {$stable(sd)}
}

puts "=== A: the check alone"
foreach {d engine} {16 informal-kind 16 informal-ic3 4 informal-ic3} {
  puts "--- DEPTH $d"
  tracked $fifo $d
  assert -name a_integrity $a_integrity
  if {$d == 4} {cover -name c_head {in_q && ahead == '0}}
  one $engine 5s -all
  expect [expr {$d == 4 ? "proven" : "undetermined"}] a_integrity
  if {$d == 4} {expect covered c_head}
}

puts "=== B: the slot helper, alone, DEPTH 16"
tracked $fifo 16
assert -name h_slot $helper
cover  -name c_in {in_q}
one informal-kind 5s -all
expect proven  h_slot
expect covered c_in

puts "=== C: the check with the helper assumed, DEPTH 16"
tracked $fifo 16
assume -name m_slot $helper
assert -name a_integrity $a_integrity
# The tracked word leaves with eight words behind it.
cover  -name c_out {in_q && ahead == '0 && u.do_read && u.count == 9}
one informal-kind 5s -all
expect proven   a_integrity
expect covered  c_out
expect_depth 10 c_out

puts "=== D: the read pointer steps by two"
tracked $skip 16
assert -name a_integrity $a_integrity
one informal-bmc 5s -all
expect cex     a_integrity
expect_depth 3 a_integrity
puts "verdict: integrity proven through one tracked word and one slot\
 helper, and the mutant caught"
finish
