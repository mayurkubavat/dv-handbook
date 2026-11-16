# ric3.tcl -- the comparison for hier/: the pipe of two FIFOs, DEPTH
# 16, without the parent helper, by rIC3: boxed under the contracts,
# and flat.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set files [list $rtl09/fifo_fixed.sv $here/../common/hier.sv]
foreach how {boxed flat} {
  puts "=== $how"
  if {$how eq "boxed"} {
    design $files pipe2 -parameter DEPTH 16 -bbox_m {fifo}
    foreach u {u0 u1} {
      assume -name ${u}_CE "$u.empty == ($u.g == '0)"
      assume -name ${u}_CF "$u.full == ($u.g == 16)"
    }
  } else {
    design $files pipe2 -parameter DEPTH 16
  }
  assert -name P1_A {G == '0 |-> empty}
  assert -name P2_A {full |-> G >= 16}
  one ric3-ic3 30s -all
  expect proven P1_A P2_A
}
puts "verdict: rIC3 proves the pipe boxed and flat without the helper"
finish
