// A register in another domain steering a clock multiplexer. The gating
// enable is itself a crossing, @sec-ch03-clocks says; the tool sees it as
// the receiving register's clock depending on both domains, which fails
// the gate, rather than as a line of its own.
module clock_mux_select_register (input logic clk1, clk2, en, m,
                                  input logic [7:0] d, 
               output logic [7:0] q);
  logic gclk, mclk, mode;
  logic [7:0] a, b;
  always_ff @(posedge clk2) mode <= m;     // clk2-domain control
  assign gclk = clk1 & en;
  assign mclk = mode ? clk1 : gclk;        // steered from clk2
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge mclk) b <= a;
  assign q = b;
endmodule
