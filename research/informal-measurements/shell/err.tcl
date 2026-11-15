clear -all
analyze -sv12 [file dirname [info script]]/../forms/probe.sv
elaborate -top probe
clock clk
reset -expression {rst}
assert -name a_bad {nosuch}
prove -all
