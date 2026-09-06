// tb_top.sv -- top module: clock, DUT, interface, and the call to run_test().
`timescale 1ns/1ps
module tb_top;
  import uvm_pkg::*;
  import counter_pkg::*;

  logic clk = 0;
  always #5 clk = ~clk;

  counter_if cif (.clk);
  counter dut (.clk, .rst_n(cif.rst_n), .en(cif.en), .count(cif.count));

  initial begin
    uvm_config_db#(virtual counter_if)::set(null, "*", "vif", cif);
    run_test();                     // test name comes from +UVM_TESTNAME
  end
endmodule
