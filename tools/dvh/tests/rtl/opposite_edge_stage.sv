// opposite_edge_stage.sv -- a two-flop chain that is not a synchronizer.
//
// The second stage samples the opposite clock edge, so the first is given
// half a clock period to settle rather than a full one. Clock polarity was
// read nowhere in these tools, so the shape was recognized as a synchronizer.
module opposite_edge_stage (input logic aclk, bclk, rst_n, d, output logic q);
  logic src, m1, m2;
  always_ff @(posedge aclk or negedge rst_n)
    if (!rst_n) src <= 1'b0; else src <= d;
  always_ff @(posedge bclk or negedge rst_n)
    if (!rst_n) m1 <= 1'b0; else m1 <= src;
  always_ff @(negedge bclk or negedge rst_n)
    if (!rst_n) m2 <= 1'b0; else m2 <= m1;
  always_ff @(posedge bclk or negedge rst_n)
    if (!rst_n) q <= 1'b0; else q <= m2;
endmodule
