# One engine, fixed order: is the report (minus times) and the VCD the same on every run?
clear -all
analyze -sv12 [file dirname [info script]]/../forms/probe.sv
elaborate -top probe
clock clk
reset -expression {rst}
set_prove_time_limit 10s
if {[info exists ::env(ENG)]} {informal::set_engines {*}$::env(ENG)}
assert -name a_max {q <= 4'd9}
assert -name a_wrong {q != 4'd9}
assert -name a_y {a |=> y}
cover -name c_seq {a ##1 b ##1 !a ##2 done}
prove -all
