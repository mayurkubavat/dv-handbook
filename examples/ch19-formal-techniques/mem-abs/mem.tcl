# mem.tcl -- one symbolic slot in place of a 256-word array. A: the
# whole design; B: the storage black-boxed and its contract at the
# slot assumed; C: the box without the contract; D: the contract
# proved on the real storage, alone and with a helper that names the
# array word at the slot; E: the forwarding bug, under the box and in
# a whole design of 16 words.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set f $here/mem_abs.sv

# The pieces, each typed once. sa is a free input held constant by
# m_sa; a_read is the property; c_read its witness cover; the contract
# pins the storage's read data at sa; the helper says the array word
# at sa is the shadow.
set m_sa     {$stable(sa)}
set a_read   {chk_q |-> rdata == exp_q}
set c_read   {chk_q && sv_ok && we}
set contract {mchk_q |-> u_ram.m_rdata == mexp_q}
set helper   {sv_ok |-> u_ram.u_mem.m[sa] == sv}
proc props {} {
  assume -name m_sa   $::m_sa
  assert -name a_read $::a_read
  cover  -name c_read $::c_read
}

puts "=== A: the whole design, 256 words"
design $f mem_top -parameter AW 8
props
one informal-kind 5s -all
expect undetermined a_read
expect covered      c_read

puts "=== B: storage black-boxed, contract assumed"
design $f mem_top -parameter AW 8 -bbox_m {mem_store}
props
assume -name m_store $contract
one informal-kind 5s -all
expect proven  a_read
expect covered c_read

puts "=== C: storage black-boxed, no contract"
design $f mem_top -parameter AW 8 -bbox_m {mem_store}
props
one informal-kind 5s -all
expect cex     a_read
expect_depth 3 a_read

puts "=== D: the contract, proved on the real storage"
design $f mem_top -parameter AW 8
assume -name m_sa $m_sa
assert -name a_store $contract
one informal-kind 5s -all
expect undetermined a_store
puts "--- the helper, alone"
design $f mem_top -parameter AW 8
assume -name m_sa $m_sa
assert -name h_mem $helper
one informal-kind 20s -all
expect proven h_mem
puts "--- the contract with the helper assumed"
design $f mem_top -parameter AW 8
assume -name m_sa $m_sa
assume -name m_mem $helper
assert -name a_store $contract
one informal-kind 20s -all
expect proven a_store

puts "=== E: the forwarding bug (BUG = 1)"
design $f mem_top -parameter AW 8 -parameter BUG 1 -bbox_m {mem_store}
props
assume -name m_store $contract
one informal-kind 5s -all
expect cex     a_read
expect_depth 3 a_read
puts "--- the whole design, 16 words"
design $f mem_top -parameter AW 4 -parameter BUG 1
props
one informal-kind 5s -all
expect cex     a_read
expect_depth 3 a_read
puts "verdict: 256 words proven through one slot, its contract proven\
 on the storage, and the bug found both ways"
finish
