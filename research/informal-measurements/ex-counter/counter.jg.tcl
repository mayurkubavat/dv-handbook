# JasperGold-style FPV setup for the counter (runs unchanged under informal).
clear -all
analyze -sv12 [file join [file dirname [info script]] counter.sv]
elaborate -top counter
clock clk
reset -expression {!rst_n}
set_prove_time_limit 60s

assert -name a_max     {q <= 4'd9}
assert -name a_step    {en && !done |=> q == $past(q) + 4'd1}
assert -name a_hold    {!en |=> $stable(q)}
assert -name a_never9  {q != 4'd9}
assert -name a_no_wrap {!wrap}
cover  -name c_done    {$rose(done)}
cover  -name c_10      {q == 4'd10}
assume -name m_en_burst {en |=> en}

prove -all
foreach p [get_property_list -include {type assert status proven}] { puts "PROVEN $p" }
