# init.tcl -- start from every state an invariant allows, not from
# reset. P is the previous chapter's pointer property; H its helper;
# INV is H with the count in range. A: a mutant whose count wraps one
# push short of full, from reset; B: the mutant from INV states;
# C: the correct FIFO from INV states, and its side conditions; D: a
# weaker start set; E: the full FIFO as a cover, from reset and from
# INV states.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set iv  $here/iv.sv
set wrap [mutant fifo_wrap $rtl09/fifo_fixed.sv \
    {s/2'b10:   count <= count + 1'b1;/2'b10:   count <= (count ==\
 (PTR_W+1)'(DEPTH-2)) ? '0 : count + 1'b1;/}]
set ok  [list $rtl09/fifo_fixed.sv $iv]
set bad [list $wrap $iv]
set P   {empty |-> u.wr_ptr == u.rd_ptr}
set H   {u.count[$clog2(DEPTH)-1:0] == u.wr_ptr - u.rd_ptr}
set INV "$H && u.count <= DEPTH"
# The witness cover of P: the FIFO becomes empty after holding words.
set C   {empty && !$past(empty)}

# from_inv FILES DEPTH START -- a new session with the shell's reset
# off, so that every register without an initial value is free in
# the first cycle, and START
# assumed in that cycle only (first is 1 there and 0 after).
proc from_inv {files d start} {
  clear -all
  analyze -sv12 {*}$files
  elaborate -top iv_top -parameter DEPTH $d
  clock clk
  reset -none
  assume -name M_start "first |-> ($start)"
}

puts "=== A: the mutant from reset"
foreach d {16 256} {
  design $bad iv_top -parameter DEPTH $d
  assert -name P_A $P
  one informal-bmc 5s -all
  if {$d == 16} {
    expect cex P_A
    expect_depth 16 P_A
  } else {
    expect undetermined P_A
  }
}

puts "=== B: the mutant from INV states, DEPTH 256"
from_inv $bad 256 $INV
assert -name P_A $P
one informal-bmc 5s -all
expect cex     P_A
expect_depth 1 P_A

puts "=== C: the correct FIFO from INV states"
puts "--- DEPTH 16, induction and IC3"
from_inv $ok 16 $INV
assert -name P_A $P
one informal-kind 5s -all
expect undetermined P_A
from_inv $ok 16 $INV
assert -name P_A $P
cover  -name P_C $C
one informal-ic3 5s -all
expect proven  P_A
expect covered P_C
puts "--- DEPTH 256, induction with the helper assumed in every cycle"
from_inv $ok 256 $INV
assume -name M_H $H
assert -name P_A $P
cover  -name P_C $C
one informal-kind 5s -all
expect proven  P_A
expect covered P_C
puts "--- the side conditions: INV holds from reset, and is inductive"
design $ok iv_top -parameter DEPTH 256
assert -name INV_A $INV
one informal-kind 5s -all
expect proven INV_A
from_inv $ok 256 $INV
assert -name INV_A $INV
one informal-kind 5s -all
expect proven INV_A

puts "=== D: a weaker start set (the count in range only), DEPTH 256"
from_inv $ok 256 {u.count <= DEPTH}
assert -name P_A $P
one informal-bmc 5s -all
expect cex     P_A
expect_depth 0 P_A

puts "=== E: the FIFO full, as a cover, DEPTH 256"
design $ok iv_top -parameter DEPTH 256
cover -name Full_C {full}
one informal-bmc 20s -all
expect covered    Full_C
expect_depth 257  Full_C
from_inv $ok 256 $INV
cover -name Full_C {full}
one informal-bmc 20s -all
expect covered  Full_C
expect_depth 0  Full_C
puts "verdict: a bug 255 pushes deep found at depth 1 from INV states,\
 with INV proven from reset and inductive"
finish
