// A clock that only ever appears gated, reaching the gate through a latch
// it holds open. Neither a port nor a register is demoted at the gate --
// the latch's output is -- so the hidden-clock report traces a demoted
// latch through its inputs, as it does a register through its timing
// pins, and names the clock.
module hidden_clock_via_latch (input logic clk1, hclk, x, input logic [7:0] d,
                 output logic [7:0] q);
  logic flag, gclk;
  logic [7:0] a, b;
  always_latch if (hclk) flag = x;
  assign gclk = clk1 & flag;
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;
  assign q = b;
endmodule
