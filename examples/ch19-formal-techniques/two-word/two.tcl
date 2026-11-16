# two.tcl -- order, loss of identity and duplication through the
# book's FIFO, checked with two symbolic words, DEPTH 4. A: the
# position form alone; B: helpers that name the slot of each tracked
# word, with the ordering of the two, proved alone; C: both forms
# with the helpers assumed; D: a mutant that reads a word twice.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set fifo $rtl09/fifo_fixed.sv
set dup [mutant fifo_dup $fifo \
    {s/      if (do_read) begin/      if (do_read \&\& !do_write) begin/}]

# env -- d1 and d2 held and distinct; d1 pushed at most once, d2 at
# most once and after d1. Every other push carries another value.
proc env {} {
  assume -name m_d    {$stable(d1) && $stable(d2) && d1 != d2}
  assume -name m_one1 {push1 |-> !in1}
  assume -name m_one2 {push2 |-> in1 && !in2}
}
# The flag form: each word comes out at most once, after it went in,
# and d2 only after d1.
proc flags {} {
  assert -name a_order {pop2 |-> out1}
  assert -name a_once1 {pop1 |-> in1 && !out1}
  assert -name a_once2 {pop2 |-> in2 && !out2}
}
# The position form: a tracked word with no word ahead of it is at
# the head, and d1 has fewer words ahead of it than d2.
proc position {} {
  assert -name p_head1 {in1 && !out1 && a1 == '0 |-> rd_data == d1}
  assert -name p_head2 {in2 && !out2 && a2 == '0 |-> rd_data == d2}
  assert -name p_ahead {in1 && !out1 && in2 && !out2 |-> a1 < a2}
}
# The helpers, typed once: the slot a1 places past the read pointer
# holds d1 while d1 is inside, likewise for d2, the previous
# chapter's pointer helper, and the ordering itself.
set slot1 {!(in1 && !out1)
           || u.mem[u.rd_ptr + a1[$clog2(DEPTH)-1:0]] == d1
              && a1 < u.count}
set slot2 {!(in2 && !out2)
           || u.mem[u.rd_ptr + a2[$clog2(DEPTH)-1:0]] == d2
              && a2 < u.count}
set ptrs  {u.count[$clog2(DEPTH)-1:0] == u.wr_ptr - u.rd_ptr
           && u.count <= DEPTH}
set order {!(in1 && !out1 && in2 && !out2) || a1 < a2}
set helper "($slot1) && ($slot2) && ($ptrs) && ($order)"

# words FILE -- a new session on the wrapper at DEPTH 4.
proc words {file} {
  design [list $file $::here/two_word.sv] two_word -parameter DEPTH 4
  env
}

puts "=== A: the position form alone"
words $fifo
position
one informal-kind 5s -all
expect undetermined p_head1 p_head2 p_ahead

puts "=== B: the slot helpers and the ordering, alone"
words $fifo
assert -name h_slots $helper
cover  -name c_inside {in1 && !out1 && in2 && !out2}
one informal-kind 5s -all
expect proven  h_slots
expect covered c_inside

puts "=== C: both forms, the helpers assumed"
words $fifo
assume -name m_slots $helper
position
flags
cover -name c_both {pop2 && out1}
cover -name c_inside {in1 && !out1 && in2 && !out2}
one informal-kind 5s -all
expect proven       p_head1 p_head2 p_ahead a_order
expect undetermined a_once1 a_once2
expect covered      c_both c_inside
expect_depth 3      c_both c_inside

puts "=== D: the mutant that reads a word twice"
words $dup
position
flags
one informal-bmc 5s -all
expect cex p_head1 p_head2 p_ahead a_order a_once1 a_once2
puts "verdict: order proven by position with slot helpers; the flag\
 form's once-only checks still need an invariant over every slot"
finish
