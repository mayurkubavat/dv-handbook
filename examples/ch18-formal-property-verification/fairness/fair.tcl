# fair.tcl -- two promises and three environments. "Eventually
# granted" and "granted within four cycles" are each checked with no
# assumption, with a fairness assumption, and with a bound on the
# environment. One property to a session, because another property's
# bookkeeping state would lengthen the loop that is printed.
set here [file dirname [info script]]
source $here/../common/proof.tcl

set eventual {req && n == 2'd0 |-> s_eventually gnt}
set bounded  {req && n == 2'd0 |-> ##[1:4] gnt}

# session ENGINE PROPERTY ASSUMPTION -- a fresh session with one
# assertion a_grant and at most one assumption.
proc session {engine property assumption} {
  clear -all
  analyze -sv12 $::here/../lasso/live_small.sv
  elaborate -top live_small
  clock clk
  reset -expression {rst}
  assert -name a_grant $property
  if {$assumption ne ""} {assume -name m_env $assumption}
  one $engine 20s -all
}

puts "=== eventually granted; no assumption"
session informal-ic3 $eventual {}
expect cex a_grant
expect_depth 4 a_grant
puts "=== eventually granted; fairness: assume {s_eventually !stall}"
session informal-ic3 $eventual {s_eventually !stall}
expect proven a_grant
puts "=== eventually granted; a bound: assume {stall |=> !stall}"
session informal-ic3 $eventual {stall |=> !stall}
expect proven a_grant

puts "=== granted within four cycles; no assumption"
session informal-kind $bounded {}
expect cex a_grant
expect_depth 5 a_grant
puts "=== granted within four cycles; fairness"
session informal-kind $bounded {s_eventually !stall}
expect cex a_grant
expect_depth 5 a_grant
puts "=== granted within four cycles; the bound"
session informal-kind $bounded {stall |=> !stall}
expect proven a_grant
puts "verdict: fairness proves the eventual form only; the bounded\
 environment proves both"
finish
