// clk2 reaches the blend through a cell the clock walk's pass-through set
// did not list -- an exclusive-nor, written `~^`. Any combinational cell
// carries a clock dependency; a list of cell types is wrong the first time
// a design uses one it did not anticipate.
module xnor_clock_blend (input logic clk1, clk2, pol, input logic [7:0] d,
                output logic [7:0] q, output logic t);
  logic clk2p, gclk, tog;
  logic [7:0] a, b;
  assign clk2p = clk2 ~^ pol;             // polarity-selectable clk2
  assign gclk  = clk1 & clk2p;            // blend
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;
  always_ff @(posedge clk2p) tog <= ~tog; // clk2p clocks registers
  assign q = b;
  assign t = tog;
endmodule
