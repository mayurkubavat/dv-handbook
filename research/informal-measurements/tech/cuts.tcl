source [file dirname [info script]]/common.tcl
setup handshake.sv handshake
set_prove_time_limit 20s
assert -name a_hold_q   {busy |=> $stable(q)}
assert -name a_gnt_once {gnt |=> !gnt}
assert -name a_no_early {$rose(busy) |=> !gnt}
cover  -name c_gnt      {gnt}
puts "--- whole design"; prove -all
puts "--- stopat u_timer.expired"
stopat u_timer.expired
prove -all
puts "stopat -list: [stopat -list]"
stopat -clear
puts "--- stopat u_timer.t (the 16-bit register)"
stopat u_timer.t
prove -all
stopat -clear
puts "--- black box: elaborate -bbox_m {timer}"
setup handshake.sv handshake -bbox_m {timer}
set_prove_time_limit 20s
assert -name a_hold_q   {busy |=> $stable(q)}
assert -name a_gnt_once {gnt |=> !gnt}
assert -name a_no_early {$rose(busy) |=> !gnt}
cover  -name c_gnt      {gnt}
prove -all
catch {assert -name a_in {u_timer.t <= 16'd200}} msg; puts "name inside box: $msg"
