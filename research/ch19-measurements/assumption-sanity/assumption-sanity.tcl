# assumption-sanity.tcl -- assumptions that end traces. A: none;
# B: an assumption every trace runs into (the counter must not reach
# 5); C: one that only the mode-1 traces run into. In each, a false
# assertion, a deep cover of time, and a witness cover for the
# assertion.
set here [file dirname [info script]]
source $here/../common.tcl
set f $here/sanity.sv
proc body {} {
  assert -name A_mode {mode && chosen |-> cnt != 4'd9}
  cover  -name Deep_C {t == 6'd50}
  cover  -name Witness_C {mode && chosen && cnt == 4'd8}
}
puts "=== A: no assumption"
design $f sanity
body
one informal-kind 30s -all
expect cex A_mode
puts "=== B: every trace ends at cnt == 5"
design $f sanity
assume -name M_dead {cnt != 4'd5}
body
one informal-kind 30s -all
puts "=== C: mode-1 traces end at cnt == 5"
design $f sanity
assume -name M_dead1 {mode && chosen |-> cnt != 4'd5}
body
one informal-kind 30s -all
finish
