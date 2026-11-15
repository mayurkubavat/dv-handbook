source [file dirname [info script]]/common.tcl
setup handshake.sv handshake
set_prove_time_limit 60s
assert -name a_live      {req && !busy |-> s_eventually gnt}
assert -name a_bounded   {req && !busy |-> ##[1:201] gnt}
assert -name a_tooshort  {req && !busy |-> ##[1:200] gnt}
assert -name a_always_g  {s_eventually gnt}
foreach e {{} informal-kind informal-ic3 informal-bmc ric3-ic3} {
  puts "--- engines {$e}"; informal::set_engines {*}$e
  set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
}
informal::set_engines
puts "--- with fairness assume {s_eventually req}"
assume -name m_fair {s_eventually req}
prove -all
