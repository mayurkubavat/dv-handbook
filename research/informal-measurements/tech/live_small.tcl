source [file dirname [info script]]/common.tcl
setup live_small.sv live_small
set_prove_time_limit 20s
assert -name a_live   {req && n == 2'd0 |-> s_eventually gnt}
assert -name a_idle   {s_eventually gnt}
assert -name a_step   {n == 2'd1 |-> s_eventually n == 2'd2}
assert -name a_until  {n == 2'd1 |=> (n == 2'd2) s_until gnt}
assert -name a_wuntil {n == 2'd1 |=> (n == 2'd2) until gnt}
foreach e {{} informal-bmc informal-kind informal-ic3 ric3-ic3} {
  puts "--- engines {$e}"; informal::set_engines {*}$e
  set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
}
informal::set_engines
puts "--- fairness: assume {s_eventually !stall}"
assume -name m_fair {s_eventually !stall}
prove -all
puts "--- same session plus a wide bounded property"
assert -name a_wide {req && n == 2'd0 |-> ##[1:300] (gnt || stall || 1'b1)}
informal::set_engines informal-bmc
prove -property a_idle
