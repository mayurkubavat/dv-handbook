// A clock and a gated copy of it selected by a second clock. The data
// inputs depend on one clock and would pass as a bypass multiplexer; the
// select depends on another, and makes it a blend.
module clock_mux_select_gated (input logic clk1, clk2, en, input logic [7:0] d,
                output logic [7:0] q, output logic t);
  logic gclk, mclk, tog;
  logic [7:0] a, b;
  assign gclk = clk1 & en;
  assign mclk = clk2 ? clk1 : gclk;
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge mclk) b <= a;        // 8 bits, no synchronizer
  always_ff @(posedge clk2) tog <= ~tog;
  assign q = b;
  assign t = tog;
endmodule
