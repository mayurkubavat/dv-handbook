# ag.tcl -- each block proved under the other's guarantee, then the
# ring. A: safety, one block with its neighbor's guarantee assumed,
# and a block whose reset value breaks its own guarantee; B: the
# safety ring, flat; C: liveness, one block under its neighbor's
# "eventually", and a false liveness assertion that a satisfiable
# fairness assumption must leave refutable; D: the liveness ring,
# flat; E: the ring with both resets at 1, where each block's lemma,
# proved on the ring itself with the other's assumed, is "proven".
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f $here/ag.sv

puts "=== A: safety, one block, its neighbor's guarantee assumed"
foreach r {0 1} {
  puts "--- RST1 = $r"
  design $f blk -parameter RST1 $r
  assume -name M_in  {in == 1'b0}
  assert -name G_out {out == 1'b0}
  cover  -name C_run {rst_n && $past(rst_n)}
  one informal-kind 5s -all
  expect [expr {$r ? "cex" : "proven"}] G_out
  expect covered C_run
  if {$r} {expect_depth 1 G_out}
}
puts "=== B: safety, the ring"
design $f ag_top
assert -name G_x {x == 1'b0}
assert -name G_y {y == 1'b0}
one informal-kind 5s -all
expect proven G_x G_y
puts "=== C: liveness, one block, its neighbor's guarantee assumed"
design $f blk
assume -name M_in  {s_eventually in}
assert -name G_out {s_eventually out}
assert -name G_none {s_eventually 1'b0}
cover  -name C_out {out}
one informal-ic3 5s -all
expect proven  G_out
expect cex     G_none
expect covered C_out
puts "=== D: liveness, the ring"
design $f ag_top
assert -name G_x {s_eventually x}
one informal-ic3 5s -all
expect cex     G_x
expect_depth 3 G_x
puts "=== E: safety, the ring with both resets at 1, lemma for lemma"
foreach {m g} {{} x y x x y} {
  puts "--- assert $g == 0, [expr {$m eq "" ? "alone" : "assume $m == 0"}]"
  design $f ag_top -parameter RST1 1
  if {$m ne ""} {assume -name L_M "$m == 1'b0"}
  assert -name L_A "$g == 1'b0"
  cover  -name C_run {rst_n && $past(rst_n)}
  one informal-kind 5s -all
  if {$m eq ""} {
    expect cex         L_A
    expect covered     C_run
    expect_depth 1     L_A
  } else {
    expect proven      L_A
    expect unreachable C_run
  }
}
puts "verdict: the circular argument holds for safety, block by block,\
 and fails for liveness, where the ring never starts, and for lemmas\
 proved on one design"
finish
