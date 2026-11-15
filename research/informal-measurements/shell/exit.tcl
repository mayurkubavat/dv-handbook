clear -all
analyze -sv12 [file dirname [info script]]/../forms/probe.sv
elaborate -top probe
clock clk
reset -expression {rst}
set_prove_time_limit 5s
informal::set_engines informal-kind
assert -name a_max {q <= 4'd9}
assert -name a_wrong {q != 4'd9}
set r [prove -all]
report
puts "returned: $r"
puts "cex list: [get_property_list -include {status cex}]"
set f [open [file dirname [info script]]/../build/session.json w]; puts $f [informal::session]; close $f
if {[dict get $r cex] > 0} { exit 3 }
