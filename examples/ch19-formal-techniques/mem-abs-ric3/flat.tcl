# flat.tcl -- the comparison for the memory abstraction: the whole
# design, no box and no contract, proved by rIC3 at 16 and 256 words.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f $here/../mem-abs/mem_abs.sv
foreach aw {4 8} {
  puts "=== the whole design, [expr {1 << $aw}] words"
  design $f mem_top -parameter AW $aw
  assume -name m_sa   {$stable(sa)}
  assert -name a_read {chk_q |-> rdata == exp_q}
  cover  -name c_read {chk_q && sv_ok && we}
  one ric3-ic3 30s -all
  expect proven  a_read
  expect covered c_read
}
puts "verdict: the flat design proven by rIC3 at both sizes"
finish
