# assume.tcl -- assumptions as constraints: none, a partial
# over-constraint, a contradiction, and a contradiction that needs
# two cycles to show. One engine, so the report repeats.
source [file dirname [info script]]/common.tcl
clear -all
analyze -sv12 $here/handshake.sv
elaborate -top handshake
clock clk
reset -expression {rst}
set_prove_time_limit 20s
informal::set_engines informal-ic3
assert -name a_gnt_after_busy {gnt |-> $past(busy)}
assert -name a_false          {!gnt}
cover  -name c_gnt            {gnt}
cover  -name c_busy           {busy}
cover  -name c_true           {1'b1}
puts "--- no assumptions"; prove -all
puts "--- partial over-constraint: assume {!req}"
assume -name m_noreq {!req}
prove -all
assume -remove m_noreq
puts "--- contradiction in one cycle: assume {d < 4'd8} and {d > 4'd9}"
assume -name m_lo {d < 4'd8}
assume -name m_hi {d > 4'd9}
prove -all
assume -remove m_lo m_hi
puts "--- contradiction that needs state: assume {req} and {busy |-> !req}"
assume -name m_req  {req}
assume -name m_idle {busy |-> !req}
prove -all
puts "--- the same under bounded model checking alone"
informal::set_engines informal-bmc
set_prove_time_limit 5s
prove -all
