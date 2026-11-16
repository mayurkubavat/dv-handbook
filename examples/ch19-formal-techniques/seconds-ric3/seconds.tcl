# seconds.tcl -- the runs that seconds.py times: the rows with a
# verdict from mem-abs, hier and hier-ric3, case-split and
# history-ric3, each in a session of its own with one assertion, one
# engine and a limit of sixty seconds. Each run prints a line
# "run|KEY|ENGINE|NAME" and then the tool's table, whose time column
# the book's wrapper removes from what it prints and keeps in the
# file seconds.py reads.
set here [file dirname [info script]]
source $here/../common/ch19.tcl
set limit 60s
set mem  $here/../mem-abs/mem_abs.sv
set pipe [list $rtl09/fifo_fixed.sv $here/../common/hier.sv]
set hp   [list $rtl09/fifo_fixed.sv $here/../history/hp.sv]

# run KEY ENGINE NAME -- prove the one assertion NAME of this session.
proc run {key engine name} {
  puts "run|$key|$engine|$name"
  one $engine $::limit -property [full $name]
}

# Memory abstraction, 256 words unless the key says 16.
proc ram {aw args} {
  design $::mem mem_top -parameter AW $aw {*}$args
  assume -name m_sa {$stable(sa)}
}
ram 8 -bbox_m {mem_store}
assume -name m_store {mchk_q |-> u_ram.m_rdata == mexp_q}
assert -name a_read {chk_q |-> rdata == exp_q}
run mem-box informal-kind a_read
ram 8
assert -name h_mem {sv_ok |-> u_ram.u_mem.m[sa] == sv}
run mem-helper informal-kind h_mem
ram 8
assume -name m_mem {sv_ok |-> u_ram.u_mem.m[sa] == sv}
assert -name a_store {mchk_q |-> u_ram.m_rdata == mexp_q}
run mem-store informal-kind a_store
foreach aw {4 8} {
  ram $aw
  assert -name a_read {chk_q |-> rdata == exp_q}
  run mem-flat$aw ric3-ic3 a_read
}

# The pipe of two FIFOs, DEPTH 16.
proc pipe2 {boxed} {
  if {$boxed} {
    design $::pipe pipe2 -parameter DEPTH 16 -bbox_m {fifo}
    foreach u {u0 u1} {
      assume -name ${u}_CE "$u.empty == ($u.g == '0)"
      assume -name ${u}_CF "$u.full == ($u.g == 16)"
    }
  } else {
    design $::pipe pipe2 -parameter DEPTH 16
  }
}
set HP {G == 6'(u0.g) + 6'(u1.g) && u0.g <= 16 && u1.g <= 16}
set P(P1_A) {G == '0 |-> empty}
set P(P2_A) {full |-> G >= 16}
pipe2 1
assert -name HP_A $HP
run pipe-hp informal-kind HP_A
foreach n {P1_A P2_A} {
  pipe2 1
  assume -name HP_M $HP
  assert -name $n $P($n)
  run pipe-under-hp informal-kind $n
}
foreach boxed {1 0} {
  foreach n {P1_A P2_A} {
    pipe2 $boxed
    assert -name $n $P($n)
    run [expr {$boxed ? "pipe-box" : "pipe-flat"}] ric3-ic3 $n
  }
}

# The multiplier miter, W = 8: whole and in four cases.
proc mul {} {
  clear -all
  analyze -sv12 $::here/../case-split/mul.sv
  elaborate -top mul_miter -parameter W 8
  clock clk
  reset -none
  assert -name A_eq {p_ref == p_arr}
}
mul
run mul-whole informal-kind A_eq
foreach c {0 1 2 3} {
  mul
  assume -name M_case "a\[7:6\] == 2'd$c"
  run mul-case$c informal-kind A_eq
}

# The k-th word through the FIFO, DEPTH 4.
design $hp proph_top
assume -name m_k {$stable(k)}
assert -name a_hist {pop_k |-> rd_data == hv}
run kth-history ric3-ic3 a_hist
design $hp proph_top
assume -name m_k     {$stable(k)}
assume -name m_pv    {$stable(pv)}
assume -name m_check {pop_k |-> rd_data == pv}
assert -name a_proph_late {pop_k |-> hv == pv}
run kth-prophecy ric3-ic3 a_proph_late
finish
