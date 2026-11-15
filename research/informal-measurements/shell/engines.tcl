clear -all
analyze -sv12 [file dirname [info script]]/../forms/probe.sv
elaborate -top probe
clock clk
reset -expression {rst}
set_prove_time_limit 5s
assert -name a_max {q <= 4'd9}
assert -name a_wrong {q != 4'd9}
cover -name c_nine {q == 4'd9}
cover -name c_ten {q == 4'd10}
foreach e {informal-bmc informal-kind informal-ic3 informal-kind-ic3 informal-ic3-mt ric3-ic3 ric3-bmc ric3 abc-pdr abc-bmc3 informal-wbmc nosuch-engine} {
  puts "--- informal::set_engines $e"
  if {[catch {informal::set_engines $e; prove -all} msg]} {puts "ERROR: $msg"}
}
puts "--- set_engine_mode {Ht}"
informal::set_engines
catch {set_engine_mode {Ht}} msg; puts $msg
prove -all
puts "--- set_engine_mode {B}"
catch {set_engine_mode {B}} msg; puts $msg
prove -all
