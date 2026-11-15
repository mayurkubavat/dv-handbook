# assume.tcl -- an assumption is part of every question the engines
# ask. One true assertion, one false one, and three covers, under no
# assumption and then under three sets of them; and the last set again
# under an engine that only searches.
set here [file dirname [info script]]
source $here/../common/proof.tcl
analyze -sv12 $here/handshake.sv
elaborate -top handshake
clock clk
reset -expression {rst}
assert -name a_gnt_after_busy {gnt |-> $past(busy)}
assert -name a_false          {!gnt}
cover  -name c_gnt            {gnt}
cover  -name c_busy           {busy}
cover  -name c_true           {1'b1}

puts "=== no assumption"
one informal-ic3 20s -all
expect proven  a_gnt_after_busy
expect cex     a_false
expect covered c_gnt c_busy c_true
expect_depth 202 a_false c_gnt

puts "=== an over-constraint: assume {!req}"
assume -name m_noreq {!req}
one informal-ic3 20s -all
expect proven      a_gnt_after_busy a_false
expect unreachable c_gnt c_busy
expect covered     c_true
assume -remove m_noreq

puts "=== a contradiction: assume {d < 4'd8} and {d > 4'd9}"
assume -name m_lo {d < 4'd8}
assume -name m_hi {d > 4'd9}
one informal-ic3 20s -all
expect proven      a_gnt_after_busy a_false
expect unreachable c_gnt c_busy c_true
assume -remove m_lo m_hi

puts "=== a contradiction that needs a cycle: assume {req}\
 and {busy |-> !req}"
assume -name m_req  {req}
assume -name m_idle {busy |-> !req}
one informal-ic3 20s -all
expect proven      a_gnt_after_busy a_false
expect unreachable c_gnt c_busy
expect covered     c_true

puts "=== the same assumptions under bounded search alone"
one informal-bmc 2s -all
expect undetermined a_gnt_after_busy a_false c_gnt c_busy
expect covered      c_true
puts "verdict: a false assertion proven under each of three\
 assumption sets, and nothing in a report says so"
finish
