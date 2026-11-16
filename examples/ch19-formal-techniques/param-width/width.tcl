# width.tcl -- parameter reduction: what a run at one DEPTH says
# about another. A: the first FIFO, whose full flag rises one entry
# early, at DEPTH 4 and 16; B: the repaired FIFO checked against a
# five-bit occupancy count at DEPTH 16 and 32; C: the repaired FIFO's
# pointers at DEPTH 4, 5 and 8, where $clog2(5) gives a pointer that
# counts to 7.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set wrap $here/pw_top.sv

puts "=== A: the first FIFO, full against the ghost count"
foreach d {4 16} {
  design [list $rtl01/fifo.sv $wrap] pw_top -parameter DEPTH $d
  assert -name Full_A "full |-> occ == $d"
  cover  -name Full_C "occ == $d"
  one informal-kind 5s -all
  expect cex         Full_A
  expect unreachable Full_C
  expect_depth $d    Full_A
}

puts "=== B: the repaired FIFO, against a five-bit count"
foreach d {16 32} {
  design [list $rtl09/fifo_fixed.sv $wrap] pw_top -parameter DEPTH $d
  assert -name NoOverflow_A "occ <= 5'($d)"
  assert -name Full_A       "full == (occ == 5'($d))"
  one informal-kind 5s -all
  expect [expr {$d == 16 ? "proven" : "cex"}] NoOverflow_A Full_A
}

puts "=== C: the repaired FIFO's pointers stay below DEPTH"
foreach d {4 5 8} {
  design $rtl09/fifo_fixed.sv fifo -parameter DEPTH $d
  assert -name Ptr_A {wr_ptr < DEPTH && rd_ptr < DEPTH}
  cover  -name Full_C {full}
  one informal-kind 5s -all
  expect [expr {$d == 5 ? "cex" : "proven"}] Ptr_A
  expect covered Full_C
}
puts "verdict: a counterexample at DEPTH 4 is the bug at 16; proofs at\
 16, and at 4 and 8, say nothing about 32 or 5"
finish
