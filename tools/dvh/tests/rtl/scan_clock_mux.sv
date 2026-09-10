// scan_clock_mux.sv -- an ordinary scan multiplexer between two clocks.
//
// `test_clk` reaches nothing in this design but the multiplexer, which is
// how a test clock is normally wired. The walk therefore found no evidence
// that it was a clock, classified it as a gating enable, and said it was
// sure; the crossing between two asynchronous clocks was then excused from
// the build gate as "one clock, gated differently" and the tool exited 0.
//
// The rule that fixes it is the chapter's own: a gate has one clock and an
// enable, a multiplexer selects between two clocks, and selection must
// never demote either input.
module scan_clock_mux (
  input  logic       clk_a, test_clk, scan_en, rst_n,
  input  logic [7:0] d,
  output logic [7:0] q, r
);
  logic cg;
  logic [7:0] src;
  assign cg = scan_en ? test_clk : clk_a;
  always_ff @(posedge clk_a or negedge rst_n)
    if (!rst_n) src <= 8'h00; else src <= d;
  always_ff @(posedge cg or negedge rst_n)
    if (!rst_n) q <= 8'h00; else q <= src;
  always_ff @(posedge clk_a or negedge rst_n)
    if (!rst_n) r <= 8'h00; else r <= d;
endmodule
