source [file dirname [info script]]/common.tcl
setup handshake.sv handshake
set_prove_time_limit 20s
assert -name a_gnt_after_busy {gnt |-> $past(busy)}
assert -name a_false          {!gnt}
cover  -name c_gnt            {gnt}
cover  -name c_busy           {busy}
puts "--- no assumptions"; prove -all
puts "--- partial over-constraint: assume {!req}"
assume -name m_noreq {!req}
prove -all
assume -remove m_noreq
puts "--- contradiction: assume {d < 4'd8} and {d > 4'd9}"
assume -name m_lo {d < 4'd8}
assume -name m_hi {d > 4'd9}
prove -all
assume -remove m_lo m_hi
puts "--- contradiction that needs state: assume {busy |-> !busy ##0 req} style: assume {req} and {!req ##1 1'b1}"
assume -name m_dead {req |=> !busy}
assume -name m_req  {req}
prove -all
