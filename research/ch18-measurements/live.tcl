# live.tcl -- liveness on a four-state design: the lasso, fairness,
# and the bounded rewrite. In-house engines only: rIC3 is not run on
# liveness properties.
source [file dirname [info script]]/common.tcl
clear -all
analyze -sv12 $here/live_small.sv
elaborate -top live_small
clock clk
reset -expression {rst}
assert -name a_live    {req && n == 2'd0 |-> s_eventually gnt}
assert -name a_step    {n == 2'd1 |-> s_eventually n == 2'd2}
assert -name a_bound4  {req && n == 2'd0 |-> ##[1:4] gnt}
puts "=== no fairness"
each_engine {informal-bmc informal-kind informal-ic3 informal-kind-ic3
             informal-ic3-mt ric3-ic3} 30s -all
puts "=== fairness: assume {s_eventually !stall}"
assume -name m_fair {s_eventually !stall}
each_engine {informal-bmc informal-kind informal-ic3} 30s -all
assume -remove m_fair
puts "=== a bounded environment instead: assume {stall |=> !stall}"
assume -name m_once {stall |=> !stall}
assert -name a_bound5  {req && n == 2'd0 |-> ##[1:5] gnt}
each_engine {informal-bmc informal-kind informal-ic3} 30s -all
