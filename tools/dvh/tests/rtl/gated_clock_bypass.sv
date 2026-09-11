// One clock, gated, with a bypass multiplexer around the gate. A selection
// between a clock and a gated copy of it is one clock; declared, the
// multiplexer's inputs depend on the same clock and it is not undecided.
module gated_clock_bypass (input logic clk, en, mode, input logic [7:0] d,
               output logic [7:0] q);
  logic gclk, mclk;
  logic [7:0] a, b;
  assign gclk = clk & en;
  assign mclk = mode ? clk : gclk;
  always_ff @(posedge clk)  a <= d;
  always_ff @(posedge mclk) b <= a;
  assign q = b;
endmodule
