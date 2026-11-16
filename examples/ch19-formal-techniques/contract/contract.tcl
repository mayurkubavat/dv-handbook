# contract.tcl -- ghost state and a contract stated on it. fifo_ctr is
# the book's FIFO with a ghost occupancy count g built from its ports.
# The contract: empty exactly when g is 0 (CE_A), full exactly when g
# is DEPTH (CF_A). The ghost helper H ties g to the FIFO's own count.
# A: DEPTH 16, all three proven; B: DEPTH 64, the contract alone, the
# helper alone, and the contract with the helper assumed.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set files [list $rtl09/fifo_fixed.sv $here/../common/hier.sv]
set H {g == u.count}

# fifo_ctr DEPTH -- a new session on one FIFO and its ghost, with the
# contract asserted.
proc fifo_ctr {d} {
  design $::files fifo_ctr -parameter DEPTH $d
  assert -name CE_A {empty == (g == '0)}
  assert -name CF_A "full == (g == $d)"
}

puts "=== A: DEPTH 16"
fifo_ctr 16
assert -name H_A $H
one informal-kind 5s -all
expect proven CE_A CF_A H_A

puts "=== B: DEPTH 64"
puts "--- the contract alone"
fifo_ctr 64
one informal-kind 5s -all
expect undetermined CE_A CF_A
puts "--- the ghost helper alone"
design $files fifo_ctr -parameter DEPTH 64
assert -name H_A $H
one informal-kind 5s -all
expect proven H_A
puts "--- the contract with the helper assumed"
fifo_ctr 64
assume -name H_M $H
one informal-kind 5s -all
expect proven CE_A CF_A
puts "verdict: the contract proven on its ghost count at 16 and, with\
 the ghost helper, at 64"
finish
