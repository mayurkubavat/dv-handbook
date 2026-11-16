# initial-value.tcl -- start from every state an invariant allows, not
# from reset. P is the previous chapter's pointer property; INV is its
# helper. A: the wrapping mutant from reset; B: the mutant from INV
# states; C: the correct FIFO from INV states, and INV itself proved
# from reset; D: a weaker start set; E: the full FIFO as a cover.
set here [file dirname [info script]]
source $here/../common.tcl
set ok  [list $::rtl09/fifo_fixed.sv $here/iv.sv]
set bad [list $here/fifo_wrap.sv $here/iv.sv]
set P   {empty |-> u.wr_ptr == u.rd_ptr}
set INV {u.count[$clog2(DEPTH)-1:0] == u.wr_ptr - u.rd_ptr && u.count <= DEPTH}
# from_inv FILES DEPTH START -- reset off, every register free in the
# first cycle, START assumed there.
proc from_inv {files d start} {
  clear -all
  analyze -sv12 {*}$files
  elaborate -top iv_top -parameter DEPTH $d
  clock clk
  reset -none
  assume -name M_start "first |-> ($start)"
}
foreach d {16 256} {
  puts "=== A: the mutant from reset, DEPTH $d"
  design $bad iv_top -parameter DEPTH $d
  assert -name P_A $P
  one informal-bmc 60s -all
}
puts "=== B: the mutant from INV states, DEPTH 256"
from_inv $bad 256 $INV
assert -name P_A $P
one informal-bmc 60s -all
expect cex P_A
puts "=== C: the correct FIFO from INV states, DEPTH 256"
from_inv $ok 256 $INV
assert -name P_A $P
one informal-kind 20s -all
one ric3-ic3 60s -all
puts "--- INV from reset (the side condition)"
design $ok iv_top -parameter DEPTH 256
assert -name INV_A $INV
one informal-kind 30s -all
expect proven INV_A
puts "=== D: a weaker start set (count <= DEPTH only), DEPTH 256"
from_inv $ok 256 {u.count <= DEPTH}
assert -name P_A $P
one informal-bmc 30s -all
expect cex P_A
puts "=== E: the FIFO full, as a cover, DEPTH 256"
design $ok iv_top -parameter DEPTH 256
cover -name Full_C {full}
one informal-bmc 60s -all
from_inv $ok 256 $INV
cover -name Full_C {full}
one informal-bmc 60s -all
finish
