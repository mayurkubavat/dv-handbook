// A black-box clock -- a phase-locked loop the netlist cannot see into --
// on a multiplexer's select. Unknown is not nothing, on a select as on a
// gate input.
(* blackbox *)
module pll (input logic ref_clk, output logic clk_out);
endmodule
module clock_mux_select_blackbox (input logic clk1, ref_clk, en,
                                  input logic [7:0] d, 
               output logic [7:0] q, output logic t);
  logic pclk, gclk, mclk, tog;
  logic [7:0] a, b;
  pll u_pll (.ref_clk(ref_clk), .clk_out(pclk));
  assign gclk = clk1 & en;
  assign mclk = pclk ? clk1 : gclk;
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge mclk) b <= a;
  always_ff @(posedge pclk) tog <= ~tog;
  assign q = b;
  assign t = tog;
endmodule
