// dut_unreset.sv -- a register nobody resets, read through an enable.
//
// `state` has no reset. `out` is updated only when `state` is non-zero, so
// what a simulator does with an unknown decides whether the bug is visible
// or invisible. That is X-optimism, and it is the mechanism Chapter 3
// named without explaining.
module dut_unreset (
  input  logic       clk,
  input  logic       go,
  output logic [7:0] out
);
  logic [7:0] state;          // deliberately never reset

  always_ff @(posedge clk)
    if (go) state <= state + 8'd1;

  always_ff @(posedge clk)
    if (state != 8'h00) out <= state;
endmodule
