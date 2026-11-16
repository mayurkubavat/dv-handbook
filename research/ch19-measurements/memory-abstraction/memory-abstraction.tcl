# memory-abstraction.tcl -- one symbolic address in place of the array.
# A: the whole design at 16 words, without and with the helper that
# names the array element at sa; B: at 256 words; C: 256 words with
# the storage black-boxed and its contract at sa assumed; D: the box
# without the contract; E: the contract itself, proved on the storage;
# F: the forwarding bug under the abstraction and in the whole design.
set here [file dirname [info script]]
source $here/../common.tcl
set f $here/mem_abs.sv
proc props {} {
  assume -name m_sa {$stable(sa)}
  assert -name a_read {chk_q |-> rdata == exp_q}
  cover  -name c_read {chk_q && sv_ok && we}
}
proc contract {} {
  assume -name m_store {mchk_q |-> u_ram.m_rdata == mexp_q}
}

proc helper {} {
  assert -name h_mem {sv_ok |-> u_ram.u_mem.m[sa] == sv}
}
puts "=== A: whole design, 16 words"
design $f mem_top -parameter AW 4
props
one informal-kind 20s -all
expect undetermined a_read
expect covered c_read
one ric3-ic3 60s -property [full a_read]
expect proven a_read
puts "--- the helper, proved alone and then assumed"
helper
assert -disable a_read
one informal-kind 20s -property [full h_mem]
expect proven h_mem
assert -disable h_mem
assert -enable a_read
assume -name m_mem {sv_ok |-> u_ram.u_mem.m[sa] == sv}
one informal-kind 20s -property [full a_read]
expect proven a_read

puts "=== B: whole design, 256 words"
design $f mem_top -parameter AW 8
props
one informal-kind 20s -all
expect undetermined a_read
one ric3-ic3 60s -property [full a_read]
expect proven a_read
helper
one informal-kind 30s -property [full h_mem]
expect proven h_mem

puts "=== C: 256 words, storage black-boxed, contract assumed"
design $f mem_top -parameter AW 8 -bbox_m {mem_store}
props
contract
one informal-kind 30s -all
expect proven a_read
expect covered c_read

puts "=== D: 256 words, storage black-boxed, no contract"
design $f mem_top -parameter AW 8 -bbox_m {mem_store}
props
one informal-bmc 30s -all
expect cex a_read

puts "=== E: the contract as an assertion on the storage"
foreach aw {4 8} {
  design $f mem_top -parameter AW $aw
  assume -name m_sa {$stable(sa)}
  assert -name a_store {mchk_q |-> u_ram.m_rdata == mexp_q}
  one informal-kind 20s -all
  expect undetermined a_store
  one ric3-ic3 60s -all
  expect proven a_store
  assume -name m_mem {sv_ok |-> u_ram.u_mem.m[sa] == sv}
  one informal-kind 20s -all
  expect proven a_store
}

puts "=== F: the forwarding bug"
design $f mem_top -parameter AW 8 -parameter BUG 1 -bbox_m {mem_store}
props
contract
one informal-bmc 30s -all
expect cex a_read
design $f mem_top -parameter AW 4 -parameter BUG 1
props
one informal-bmc 30s -all
expect cex a_read
finish
