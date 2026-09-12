// dut_reg.sv -- a register with an asynchronous, active-low reset.
//
// The reset value is deliberately not zero. A two-state testbench starts
// every variable at zero, and zero is a legal value for a reset line, so a
// reset that never asserts leaves this register holding zero -- which is
// indistinguishable from "working" unless the reset value is something
// else. Here it is 8'hA5, so a missed reset is visible.
//
// The reset is asynchronous, so a clock edge during the pulse would load
// the value anyway through the level test in the block. The testbenches
// therefore pulse the reset before the first clock edge: what loads the
// register then is the `negedge rst_n` event, or nothing.
module dut_reg (
  input  logic       clk,
  input  logic       rst_n,
  input  logic [7:0] d,
  output logic [7:0] q
);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) q <= 8'hA5;
    else        q <= d;
endmodule
