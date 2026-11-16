# sym.tcl -- one port proved, or all of them. A: the round-robin
# arbiter with a free start: port 0, the rotation check, and the
# reset state inside the free start; B: the arbiter as the DMA builds
# it, `last` reset to 3: four proofs, and the rotation check refuted;
# C: fixed priority; D: the DMA's two channels, one invariant each.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f $here/rr_arb.sv

# arb ROUND FREE PORTS -- a new session on the arbiter; for each port
# in PORTS, a request held until granted (assumed) is granted within
# four cycles (asserted).
proc arb {round free ports} {
  design $::f rr_arb -parameter ROUND $round -parameter FREE_LAST $free
  foreach i $ports {
    assume -name m_hold$i "req\[$i\] && !gnt\[$i\] |=> req\[$i\]"
    assert -name a_wait$i \
        "req\[$i\] && !gnt\[$i\] |-> ##\[1:4\] gnt\[$i\]"
  }
}
set rot {gnt1 == {gnt0[2:0], gnt0[3]}}

puts "=== A: round robin, free start"
puts "--- port 0"
arb 1 1 0
one informal-kind 10s -all
expect proven a_wait0
puts "--- the rotation check: rotated requests give rotated grants"
design $f rr_rot -parameter FREE_LAST 1
assume -name m_rot {first |-> u1.last == u0.last + 2'd1}
assert -name a_rot $rot
cover  -name c_start {first && u0.last == 2'd1}
one informal-kind 10s -all
expect proven  a_rot
expect covered c_start
puts "--- the reset state is one of the free starts"
design $f rr_arb -parameter FREE_LAST 1
assert -name a_gnt0  {$past(!rst_n) |-> gnt == '0}
cover  -name c_reset {$past(!rst_n) && last == 2'd3}
one informal-kind 10s -all
expect proven  a_gnt0
expect covered c_reset

puts "=== B: round robin, last reset to 3"
arb 1 0 {0 1 2 3}
one informal-kind 10s -all
expect proven a_wait0 a_wait1 a_wait2 a_wait3
puts "--- the rotation check, both copies reset"
design $f rr_rot -parameter FREE_LAST 0
assert -name a_rot $rot
one informal-kind 10s -all
expect cex a_rot

puts "=== C: fixed priority"
arb 0 0 {0 1 2 3}
one informal-kind 10s -all
expect proven  a_wait0
expect cex     a_wait1 a_wait2 a_wait3
expect_depth 5 a_wait1 a_wait2 a_wait3

puts "=== D: DMA version 2, each channel proved on its own"
clear -all
analyze -sv12 $rtl11/dma_regs_pkg.sv $rtl11/dma_v2.sv
elaborate -top dma_v2
clock PCLK
reset -expression {!PRESETn}
foreach c {0 1} {
  assert -name a_excl$c "!(busy\[$c\] && done\[$c\])"
}
one informal-kind 10s -all
expect proven a_excl0 a_excl1
puts "verdict: a symmetry argument holds for the free start, which\
 covers reset; with last reset to 3 every port needs its own proof"
finish
