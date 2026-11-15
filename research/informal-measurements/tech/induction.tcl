source [file dirname [info script]]/common.tcl
# 1. BMC: a counterexample at depth 21 (cnt == 20), and no verdict on a true property
setup wrap.sv wrap
assert -name a_never20 {cnt != 32'd20}
assert -name a_small   {cnt < 32'd1000000}
with informal-bmc 5s {prove -all}
# 2. k-induction proves the inductive one, not the other
assert -name a_notbad  {cnt != 32'd3000000}
with informal-kind 20s {prove -all}
# 3. the helper as an assumption... and proved on its own (assume-guarantee by hand)
puts "--- helper a_small proved first, then assumed"
assume -name h_small {cnt < 32'd1000000}
with informal-kind 20s {prove -property a_notbad}
assume -remove h_small
# 4. IC3 needs no helper
with informal-ic3 20s {prove -property a_notbad}
with ric3-ic3 20s {prove -property a_notbad}
with informal-kind-ic3 20s {prove -property a_notbad}
with {} 20s {prove -property a_notbad}
