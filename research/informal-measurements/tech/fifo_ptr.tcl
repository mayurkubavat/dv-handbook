# "empty implies the pointers are equal" on the fixed FIFO at three depths:
# true, but only inductive together with count == wr_ptr - rd_ptr.
foreach depth {16 64 256} {
  clear -all
  analyze -sv12 /home/user/dv-handbook/examples/ch09-temporal-properties/rtl/fifo_fixed.sv
  elaborate -top fifo -parameter DEPTH $depth -parameter WIDTH 1
  clock clk
  reset -expression {!rst_n}
  set_prove_time_limit 20s
  assert -name a_empty_ptrs {empty |-> wr_ptr == rd_ptr}
  assert -name h_count      {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
  foreach e {informal-kind informal-ic3 ric3-ic3} {
    puts "=== DEPTH=$depth engine $e"
    informal::set_engines $e
    prove -all
  }
  puts "=== DEPTH=$depth informal-kind with the helper assumed"
  assert -disable h_count
  assume -name m_count {count[$clog2(DEPTH)-1:0] == wr_ptr - rd_ptr}
  informal::set_engines informal-kind
  prove -all
}
