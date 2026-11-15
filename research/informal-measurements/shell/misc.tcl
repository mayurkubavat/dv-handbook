clear -all
analyze -sv12 [file dirname [info script]]/../forms/probe.sv
catch {elaborate -top probe -create_related_covers {precondition witness}} m; puts "elaborate: $m"
clock clk
reset -expression {rst}
set_prove_time_limit 5s
assert -name a_vac {q == 4'd12 |-> done}
prove -all
clear -all
analyze -sv12 [file dirname [info script]]/misc.sv
catch {elaborate -top misc} m; puts "elaborate misc: $m"
clock clk
reset -expression {rst}
catch {prove -all} m; puts $m
