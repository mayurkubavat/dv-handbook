// Both clocks are ports and both are declared, but clk2 reaches the blend
// through a black-box clock buffer, which is the ordinary way a clock is
// distributed. The buffer's output depended on no declared clock, so the
// blend was reported as one clock gated.
(* blackbox *)
module CLKBUF (input logic I, output logic O);
endmodule

module buffered_clock_blend (input logic clk1, clk2, input logic [7:0] d,
                 output logic [7:0] q, output logic t);
  logic clk2_buf, gclk, tog;
  logic [7:0] a, b;
  CLKBUF u_buf (.I(clk2), .O(clk2_buf));
  always_ff @(posedge clk1) a <= d;          // clk1 domain
  assign gclk = clk1 & clk2_buf;             // blend clk1 with clk2
  always_ff @(posedge gclk) b <= a;          // 8 bits, no synchronizer
  always_ff @(posedge clk2_buf) tog <= ~tog; // clk2_buf clocks registers
  assign q = b;
  assign t = tog;
endmodule
