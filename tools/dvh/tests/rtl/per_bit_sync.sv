// per_bit_sync.sv -- the anti-pattern: one two-flop synchronizer per bit of
// an eight-bit value.
//
// Every chain here is individually the right shape, which is why a purely
// structural rule accepts them. Together they are a loss of data: the bits
// resolve independently, so some may arrive a cycle after the others and
// the receiver sees a value the sender never sent.
module sync1 (
  input  logic clk,
  input  logic rst_n,
  input  logic d,
  output logic q
);
  logic meta;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin meta <= 1'b0; q <= 1'b0; end
    else        begin meta <= d;    q <= meta; end
endmodule

module per_bit_sync (
  input  logic       bclk,
  input  logic       brst_n,
  input  logic       cclk,
  input  logic       crst_n,
  input  logic [7:0] cfg_in,
  output logic [7:0] acc
);
  logic [7:0] cfg_b, cfg_c;

  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) cfg_b <= 8'h00;
    else         cfg_b <= cfg_in;

  genvar i;
  generate
    for (i = 0; i < 8; i++) begin : g_sync
      sync1 u (.clk(cclk), .rst_n(crst_n), .d(cfg_b[i]), .q(cfg_c[i]));
    end
  endgenerate

  always_ff @(posedge cclk or negedge crst_n)
    if (!crst_n) acc <= 8'h00;
    else         acc <= acc + cfg_c;
endmodule
