// A divider of clk1 gated by a black-box clock: no input of the gate
// reaches a declared clock through logic alone, and one input reaches
// something the netlist cannot see into.
(* blackbox *)
module pll (input logic ref_clk, output logic clk_out);
endmodule
module divider_blackbox_blend (input logic clk1, ref_clk, input logic [7:0] d,
              output logic [7:0] q);
  logic div, pclk, gclk;
  logic [7:0] c, b;
  pll u_pll (.ref_clk(ref_clk), .clk_out(pclk));
  always_ff @(posedge clk1) div <= ~div;
  assign gclk = div & pclk;
  always_ff @(posedge div)  c <= d;     // divider domain
  always_ff @(posedge gclk) b <= c;     // divider blended with the PLL clock
  assign q = b;
endmodule
