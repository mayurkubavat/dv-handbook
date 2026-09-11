// A second clock on a multiplexer's *select*: `clk2 ? clk1 : ~clk1` is
// clk1 exclusive-nor clk2, a blend. The clock walk skipped a select
// because "a select is not a clock", which was the wrong question once the
// walk asked which clocks an input depends on; under a declaration every
// input of a gate is asked, the select included.
module clock_mux_select_clock (input logic clk1, clk2, input logic [7:0] d,
               output logic [7:0] q, output logic t);
  logic mclk, tog;
  logic [7:0] a, b;
  assign mclk = clk2 ? clk1 : ~clk1;       // = ~(clk1 ^ clk2)
  always_ff @(posedge clk1) a <= d;        // clk1 domain
  always_ff @(posedge mclk) b <= a;        // 8 bits, no synchronizer
  always_ff @(posedge clk2) tog <= ~tog;   // clk2 clocks registers too
  assign q = b;
  assign t = tog;
endmodule
