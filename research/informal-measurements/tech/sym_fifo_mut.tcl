clear -all
analyze -sv12 build/fifo_skip.sv tech/sym_fifo.sv
elaborate -top sym_fifo
clock clk
reset -expression {!rst_n}
set_prove_time_limit 60s
assume -name m_sd {$stable(sd)}
assert -name a_integrity {in_q && ahead == 5'd0 |-> rd_data == sd}
cover  -name c_out {in_q && ahead == 5'd0 && u.do_read && u.count == 5'd9}
foreach e {informal-bmc} {
  puts "=== $e"; informal::set_engines $e; prove -all
}
