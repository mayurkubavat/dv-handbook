# dma.tcl -- hs_rules bound on the DMA of the architecture case study,
# asserted on the three AXI channels it drives and assumed on the two
# it receives, all by informal-ic3. A: the six master rules, as
# Chapter 9 proved them with every input free, now under the slave's
# rules; B: a property that holds only if the slave keeps its rules,
# without them and with them.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set rules $here/../protocol/hs_rules.sv

# dma BIND -- a new session on dma_v2 with the r_first ghost bound in,
# and the files in BIND bound as well.
proc dma {bind} {
  clear -all
  analyze -sv12 $::rules $::rtl11/dma_regs_pkg.sv $::rtl11/dma_v2.sv \
      $::here/r_first.sv {*}$bind
  elaborate -top dma_v2
  clock PCLK
  reset -expression {!PRESETn}
}
# The response the DMA takes on the R handshake is the one the slave
# offered first, when it had to wait.
set rfirst {RVALID && RREADY && u_rf.wait_q |-> {RRESP, RDATA} == u_rf.first_q}
set rwait  {RVALID && RREADY && u_rf.wait_q}

puts "=== A: the six master rules, the slave's rules assumed"
dma [list $here/dma_master_bind.sv $here/dma_slave_bind.sv]
one informal-ic3 30s -all
expect proven  Held_A Stable_A
expect covered Wait_C

puts "=== B: the first response offered is the one taken"
puts "--- no rules assumed"
dma {}
assert -name RFirst_A $rfirst
cover  -name RWait_C  $rwait
one informal-ic3 30s -all
expect cex     RFirst_A
expect covered RWait_C
puts "--- the slave's rules assumed"
dma $here/dma_slave_bind.sv
assert -name RFirst_A $rfirst
cover  -name RWait_C  $rwait
one informal-ic3 30s -all
expect proven  RFirst_A
expect covered RWait_C
puts "verdict: the master rules hold under the slave's, and one\
 property holds only because of them"
finish
