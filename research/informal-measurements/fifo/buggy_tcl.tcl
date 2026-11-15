# Chapter 1 FIFO; occupancy model bound in, properties in Tcl
clear -all
analyze -sv12 /home/user/dv-handbook/examples/ch01-what-is-dv/rtl/fifo.sv [file dirname [info script]]/occ_model.sv
elaborate -top fifo
clock clk
reset -expression {!rst_n}
set_prove_time_limit 60s
assert -name FullForward_A  {u_occ.occ == 5'd16 |-> full}
assert -name FullBackward_A {full |-> u_occ.occ == 5'd16}
cover  -name FullReached_C  {u_occ.occ == 5'd16}
cover  -name Occ15_C        {u_occ.occ == 5'd15}
foreach e {{} informal-bmc informal-kind informal-ic3 informal-kind-ic3 ric3-ic3} {
  puts "--- engines: {$e}"
  informal::set_engines {*}$e
  set t [clock milliseconds]; prove -all; puts "wall [expr {[clock milliseconds]-$t}] ms"
}
