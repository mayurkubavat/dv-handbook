# decomposition.tcl -- one end-to-end property of the DMA, and the
# same property as two local ones. E2E: when channel 0 finishes
# without error, it has had as many write responses as the length it
# was started with. L1: responses plus words left equals that length,
# always. L2: when it finishes without error no words are left.
set here [file dirname [info script]]
source $here/../common.tcl
proc dma {} {
  clear -all
  analyze -sv12 $::rtl11/dma_regs_pkg.sv $::rtl11/dma_v2.sv \
      $::here/dma_wcount.sv
  elaborate -top dma_v2
  clock PCLK
  reset -expression {!PRESETn}
  assert -name E2E_A {$rose(done[0]) && !err[0] |-> u_wc.wcnt0 == u_wc.len0}
  assert -name L1_A  {u_wc.wcnt0 + wr_left[0] == u_wc.len0}
  assert -name L2_A  {$rose(done[0]) && !err[0] |-> wr_left[0] == 16'd0}
  cover  -name Done3_C {$rose(done[0]) && !err[0] && u_wc.len0 == 16'd3}
}
puts "=== A: each property alone, each engine"
foreach e {informal-kind informal-ic3 ric3-ic3} {
  dma
  one $e 60s -all
}
puts "=== B: the end-to-end property with L1 and L2 assumed"
dma
assert -disable L1_A L2_A
assume -name L1_M {u_wc.wcnt0 + wr_left[0] == u_wc.len0}
assume -name L2_M {$rose(done[0]) && !err[0] |-> wr_left[0] == 16'd0}
one informal-kind 60s -all
expect proven E2E_A
expect covered Done3_C
finish
