# sanity.tcl -- assumptions that end traces. A: none; B: an
# assumption every trace runs into (the counter must not reach 5);
# C: one that only the mode-1 traces run into. In each, a false
# assertion, a deep cover of time, and the assertion's witness cover.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f $here/sanity.sv
proc body {} {
  assert -name A_mode    {mode && chosen |-> cnt != 4'd9}
  cover  -name Deep_C    {t == 6'd50}
  cover  -name Witness_C {mode && chosen && cnt == 4'd8}
}
puts "=== A: no assumption"
design $f sanity
body
one informal-kind 5s -all
expect cex      A_mode
expect covered  Deep_C Witness_C
expect_depth 10 A_mode
puts "=== B: every trace ends at cnt == 5"
design $f sanity
assume -name M_dead {cnt != 4'd5}
body
one informal-kind 5s -all
expect proven      A_mode
expect unreachable Deep_C Witness_C
puts "=== C: mode-1 traces end at cnt == 5"
design $f sanity
assume -name M_dead1 {mode && chosen |-> cnt != 4'd5}
body
one informal-kind 5s -all
expect proven      A_mode
expect covered     Deep_C
expect unreachable Witness_C
expect_depth 51    Deep_C
puts "verdict: the deep cover passes the partial dead end; the witness\
 cover catches it"
finish
