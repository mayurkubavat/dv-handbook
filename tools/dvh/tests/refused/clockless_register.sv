// A register with no clock pin: `always_ff @($global_clock)` becomes a
// `$ff` cell, which is neither a flip-flop type nor a latch type, so the
// loop over registers never saw it. A three-register design reported two,
// and the crossing onto the third was never constructed. Refused.
module clockless_register (input logic clk1, clk2, input logic [7:0] d,
             output logic [7:0] q, output logic t);
  logic tog;
  logic [7:0] a, b;
  always_ff @(posedge clk1) a <= d;
  always_ff @($global_clock) b <= a;
  always_ff @(posedge clk2) tog <= ~tog;
  assign q = b; assign t = tog;
endmodule
