clear -all
analyze -sv12 [file dirname [info script]]/../forms/probe.sv
elaborate -top probe
clock clk
reset -expression {rst}
set_prove_time_limit 5s
assert -name a_max {q <= 4'd9}
informal::set_engines abc-pdr-pp
prove -all
