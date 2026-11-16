# assume-guarantee.tcl -- each block proved under the other's
# guarantee, then the ring. A: safety, block alone (in == 0 assumed,
# out == 0 asserted) and the broken block; B: the ring, flat;
# C: liveness, block alone (in infinitely often assumed, out
# infinitely often asserted); D: the ring, flat, the same liveness.
set here [file dirname [info script]]
source $here/../common.tcl
set f $here/ag.sv
puts "=== A: safety, one block, its neighbor's guarantee assumed"
foreach r {0 1} {
  design $f blk -parameter RST1 $r
  assume -name M_in {in == 1'b0}
  assert -name G_out {out == 1'b0}
  one informal-kind 30s -all
}
puts "=== B: safety, the ring"
design $f ag_top
assert -name G_x {x == 1'b0}
assert -name G_y {y == 1'b0}
one informal-kind 30s -all
expect proven G_x G_y
puts "=== C: liveness, one block, its neighbor's guarantee assumed"
design $f blk
assume -name M_in {s_eventually in}
assert -name G_out {s_eventually out}
one informal-ic3 30s -all
expect proven G_out
puts "=== D: liveness, the ring"
design $f ag_top
assert -name G_x {s_eventually x}
one informal-ic3 30s -all
expect cex G_x
finish
