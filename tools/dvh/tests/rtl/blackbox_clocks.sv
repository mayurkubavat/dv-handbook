// Two clocks out of one black box, on one output vector. @sec-ch03-clocks
// defines a primary clock as a design input or the output of an analog
// block treated as a black box; both of those forms can carry more than one
// clock on one net name, and a check that compared source *names* called
// these one clock and let the crossing below through the build gate.
(* blackbox *)
module blackbox_clkgen (
    input  logic ref_clk,
    output logic [1:0] clk_out
);
endmodule

module blackbox_clocks (
    input  logic ref_clk,
    input  logic rst_n,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic [1:0] c;
  logic [7:0] a, b;

  blackbox_clkgen u_pll (.ref_clk(ref_clk), .clk_out(c));

  always_ff @(posedge c[0] or negedge rst_n)
    if (!rst_n) a <= 8'h00; else a <= d;

  always_ff @(posedge c[1] or negedge rst_n)
    if (!rst_n) b <= 8'h00; else b <= a;

  assign q = b;
endmodule
