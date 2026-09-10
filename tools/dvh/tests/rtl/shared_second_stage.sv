// shared_second_stage.sv -- two chains whose second stages share a name.
//
// A two-bit value crosses on two one-bit chains, and the two second stages
// are the two bits of one declared register. Indexing the convergence rule
// by second-stage name kept one crossing per name and lost the other, so
// the rule never fired and both were reported as recognized shapes.
module shared_second_stage (input  logic aclk, arst_n, bclk, brst_n,
             input  logic [1:0] d, output logic [1:0] q);
  logic [1:0] src;
  logic       s1a, s1b;
  logic [1:0] s2;
  always_ff @(posedge aclk or negedge arst_n)
    if (!arst_n) src <= 2'b00; else src <= d;
  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) begin s1a <= 1'b0; s1b <= 1'b0; end
    else begin s1a <= src[0]; s1b <= src[1]; end
  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) s2 <= 2'b00; else s2 <= {s1b, s1a};
  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) q <= 2'b00; else q <= s2;
endmodule
