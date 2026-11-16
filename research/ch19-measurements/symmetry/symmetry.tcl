# symmetry.tcl -- one port proved, or all of them. A: the round-robin
# arbiter, bounded wait on each of four ports; B: the fixed-priority
# variant, where port 0 proves and port 3 does not; C: the DMA's two
# channels, the same per-channel invariants on each.
set here [file dirname [info script]]
source $here/../common.tcl
proc arb {round} {
  design $::here/rr_arb.sv rr_arb -parameter ROUND $round
  for {set i 0} {$i < 4} {incr i} {
    assume -name m_hold$i "req\[$i\] && !gnt\[$i\] |=> req\[$i\]"
    assert -name a_wait$i "req\[$i\] && !gnt\[$i\] |-> ##\[1:4\] gnt\[$i\]"
  }
}
puts "=== A: round robin"
arb 1
one informal-kind 30s -all
expect proven a_wait0 a_wait1 a_wait2 a_wait3
puts "=== B: fixed priority"
arb 0
one informal-kind 30s -all
expect proven a_wait0
expect cex a_wait3

puts "=== C: DMA version 2, channel 0 and channel 1"
proc dma {} {
  clear -all
  analyze -sv12 $::rtl11/dma_regs_pkg.sv $::rtl11/dma_v2.sv
  elaborate -top dma_v2
  clock PCLK
  reset -expression {!PRESETn}
  foreach c {0 1} {
    assert -name a_excl$c "!(busy\[$c\] && done\[$c\])"
    assert -name a_fly$c  "rd_fly\[$c\] |-> busy\[$c\]"
    assert -name a_room$c "in_fifo\[$c\] <= 2'd2"
    cover  -name c_done$c "done\[$c\] && !err\[$c\]"
  }
}
foreach e {informal-kind ric3-ic3} {
  dma
  one $e 60s -all
}
finish
