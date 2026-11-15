source [file dirname [info script]]/common.tcl
# The 200-cycle timer design with only liveness properties in the session
setup handshake.sv handshake
set_prove_time_limit 40s
assert -name a_live      {req && !busy |-> s_eventually gnt}
assert -name a_always_g  {s_eventually gnt}
set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
