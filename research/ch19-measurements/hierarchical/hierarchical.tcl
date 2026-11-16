# hierarchical.tcl -- prove the block's contract, then use it in place
# of the block. A: the contract on one FIFO; B: the pipe with both
# FIFOs black-boxed and the contract assumed for each; C: the same
# with half the contract; D: the pipe flat, no abstraction; E: the
# boxed pipe with the parent's own helper (G is the sum of the two
# occupancy models, each at most DEPTH) proved and then assumed.
set here [file dirname [info script]]
source $here/../common.tcl
set ff [list $::rtl09/fifo_fixed.sv $here/hier.sv]
proc pipe_props {d} {
  assert -name P1_A {G == '0 |-> empty}
  assert -name P2_A "full |-> G >= $d"
  cover  -name Both_C "u0.g == $d && u1.g == $d"
}
foreach d {16 64} {
  puts "=== A: the contract on one FIFO, DEPTH $d"
  design $ff fifo_ctr -parameter DEPTH $d
  assert -name CE_A {empty == (g == '0)}
  assert -name CF_A "full == (g == $d)"
  assert -name H_A  {g == u.count}
  one informal-kind 30s -all
  foreach n {CE_A CF_A} { one ric3-ic3 60s -property [full $n] }
  puts "--- with H_A assumed"
  assert -disable H_A
  assume -name H_M {g == u.count}
  one informal-kind 30s -all
}
foreach d {16 64 256} {
  puts "=== B: the pipe, FIFOs black-boxed, contract assumed, DEPTH $d"
  design $ff pipe2 -parameter DEPTH $d -bbox_m {fifo}
  foreach u {u0 u1} {
    assume -name ${u}_CE "$u.empty == ($u.g == '0)"
    assume -name ${u}_CF "$u.full == ($u.g == $d)"
  }
  pipe_props $d
  one informal-kind 30s -all
  foreach n {P1_A P2_A} { one ric3-ic3 60s -property [full $n] }
}
puts "=== C: half the contract (empty only), DEPTH 16"
design $ff pipe2 -parameter DEPTH 16 -bbox_m {fifo}
foreach u {u0 u1} { assume -name ${u}_CE "$u.empty == ($u.g == '0)" }
pipe_props 16
one informal-bmc 30s -all
foreach d {16 64} {
  puts "=== D: the pipe flat, DEPTH $d"
  design $ff pipe2 -parameter DEPTH $d
  pipe_props $d
  one informal-kind 30s -all
  foreach n {P1_A P2_A} { one ric3-ic3 60s -property [full $n] }
}
foreach d {16 64 256} {
  puts "=== E: boxed pipe, parent helper, DEPTH $d"
  set gw [expr {int(ceil(log($d)/log(2))) + 2}]
  set HP "G == ${gw}'(u0.g) + ${gw}'(u1.g) && u0.g <= $d && u1.g <= $d"
  design $ff pipe2 -parameter DEPTH $d -bbox_m {fifo}
  foreach u {u0 u1} {
    assume -name ${u}_CE "$u.empty == ($u.g == '0)"
    assume -name ${u}_CF "$u.full == ($u.g == $d)"
  }
  pipe_props $d
  assert -name HP_A $HP
  assert -disable P1_A P2_A
  cover -disable Both_C
  one informal-kind 30s -all
  assert -disable HP_A
  assert -enable P1_A P2_A
  cover -enable Both_C
  assume -name HP_M $HP
  one informal-kind 30s -all
}
finish
