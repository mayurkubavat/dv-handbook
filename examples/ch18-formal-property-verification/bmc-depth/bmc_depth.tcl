# bmc_depth.tcl -- what a bounded search is worth: a counterexample at
# the depth of the bug, and `undetermined` for a true property and for
# a bug beyond its reach alike.
set here [file dirname [info script]]
source $here/../common/proof.tcl

# load BUG -- the counter with its forbidden value BUG steps away.
proc load {bug} {
  clear -all
  analyze -sv12 $::here/deep.sv
  elaborate -top deep -parameter BUG $bug
  clock clk
  reset -expression {rst}
}

foreach bug {16 64 128} {
  puts "=== the forbidden value is $bug enabled steps from reset"
  load $bug
  one informal-bmc 20s -all
  expect cex a_never
  expect_depth [expr {$bug + 1}] a_never
}

puts "=== 64 again, by the engine that deepens ten frames at a time"
load 64
one informal-bmc-10 20s -all
expect cex a_never
if {[depth a_never] < 65} {
  puts "unexpected: a counterexample shorter than the shortest"
  incr ::unexpected
}
puts "its depth is not below 65: [expr {[depth a_never] >= 65}]"

puts "=== a true property: the counter never moves while en is low"
load 16
assume -name m_idle {!en}
one informal-bmc 3s -all
expect undetermined a_never

puts "=== a false one, 1024 steps away"
load 1024
one informal-bmc 3s -all
expect undetermined a_never
puts "verdict: a bug at depth 17, 65 and 129; no verdict, in the same\
 words, for a true property and for a bug 1024 steps away"
finish
