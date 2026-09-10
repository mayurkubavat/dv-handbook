// two_strong_clock_muxes.sv -- two clock muxes over the same two clocks,
// where both clocks also drive registers directly.
//
// Nothing here is ambiguous: the walk resolves both mux outputs correctly
// to the same *pair* of sources. Marking a crossing as "one clock, gated
// differently" when the two source *sets* matched therefore excused exactly
// the case that is two clocks. The test is a single shared root, not an
// equal set.
module two_strong_clock_muxes (input logic clk_a, clk_b, sel, rst_n, d,
                   output logic qa, qb, q1, q2);
  logic g1, g2;
  assign g1 = sel ? clk_a : clk_b;
  assign g2 = sel ? clk_b : clk_a;
  always_ff @(posedge clk_a or negedge rst_n)
    if (!rst_n) qa <= 1'b0; else qa <= d;
  always_ff @(posedge clk_b or negedge rst_n)
    if (!rst_n) qb <= 1'b0; else qb <= d;
  always_ff @(posedge g1 or negedge rst_n)
    if (!rst_n) q1 <= 1'b0; else q1 <= d;
  always_ff @(posedge g2 or negedge rst_n)
    if (!rst_n) q2 <= 1'b0; else q2 <= q1;
endmodule
