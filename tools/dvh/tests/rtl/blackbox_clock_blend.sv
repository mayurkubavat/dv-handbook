// A clock blended with the output of a black box: a phase-locked loop the
// netlist cannot see into, which is a primary clock by the chapter's own
// definition. It is not a port, so it cannot be declared; and a definition
// that read "depends on no declared clock" as "is control" excused the
// blend from the gate. Unknown is not nothing.
(* blackbox *)
module pll (input logic ref_clk, output logic clk_out);
endmodule

module blackbox_clock_blend (input logic clk1, ref_clk, input logic [7:0] d,
                output logic [7:0] q, output logic t);
  logic pclk, gclk, tog;
  logic [7:0] a, b;
  pll u_pll (.ref_clk(ref_clk), .clk_out(pclk));
  always_ff @(posedge clk1) a <= d;        // clk1 domain
  assign gclk = clk1 & pclk;               // blend clk1 with the PLL clock
  always_ff @(posedge gclk) b <= a;        // 8 bits, no synchronizer
  always_ff @(posedge pclk) tog <= ~tog;   // pclk is a clock elsewhere too
  assign q = b;
  assign t = tog;
endmodule
