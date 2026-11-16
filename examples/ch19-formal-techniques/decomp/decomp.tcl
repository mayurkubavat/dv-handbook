# decomp.tcl -- one end-to-end property of the DMA's channel 0, and
# the same property as two local lemmas. E2E: when the channel ends
# without error, it has had as many write responses as the length it
# was started with. L1: responses plus words left equals that length,
# always. L2: when it ends without error, no words are left. A: each
# of the three alone, by a bounded search (with the witness cover),
# by induction and by IC3; B: E2E with L1 and L2 assumed.
set here [file dirname [info script]]
source $here/../common/ch19.tcl

# The two lemmas, typed once: asserted in A, assumed in B.
set L1 {u_wc.wcnt0 + wr_left[0] == u_wc.len0}
set L2 {$rose(done[0]) && !err[0] |-> wr_left[0] == 16'd0}

# dma COVER -- a new session on dma_v2 with the ghost counts bound in,
# E2E asserted, and the witness cover when COVER is 1.
proc dma {cover} {
  clear -all
  analyze -sv12 $::rtl11/dma_regs_pkg.sv $::rtl11/dma_v2.sv \
      $::here/dma_wcount.sv
  elaborate -top dma_v2
  clock PCLK
  reset -expression {!PRESETn}
  assert -name E2E_A \
      {$rose(done[0]) && !err[0] |-> u_wc.wcnt0 == u_wc.len0}
  if {$cover} {
    cover -name Done3_C \
        {$rose(done[0]) && !err[0] && u_wc.len0 == 16'd3}
  }
}

puts "=== A: each property alone"
foreach engine {informal-bmc informal-kind informal-ic3} {
  dma [expr {$engine ne "informal-ic3"}]
  assert -name L1_A $L1
  assert -name L2_A $L2
  one $engine 5s -all
  expect undetermined E2E_A L1_A L2_A
  if {$engine ne "informal-ic3"} {
    expect covered  Done3_C
    expect_depth 15 Done3_C
  }
}

puts "=== B: E2E with L1 and L2 assumed"
dma 1
assume -name L1_M $L1
assume -name L2_M $L2
one informal-kind 5s -all
expect proven   E2E_A
expect covered  Done3_C
expect_depth 15 Done3_C
puts "verdict: the chain closes (E2E follows from L1 and L2); the\
 lemmas themselves have no verdict in 5 s"
finish
