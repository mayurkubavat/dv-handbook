// three_flop_per_bit.sv -- the per-bit anti-pattern, one flop deeper.
//
// Eight bits of one vector, each through a three-flop synchronizer, read
// together downstream. A convergence check that looked only at a
// synchronizer's immediate second stage saw nothing here, because the third
// flop sits between that stage and the register that reads them all.
module sync3 (input logic clk, rst_n, d, output logic q);
  logic m1, m2;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin m1<=0; m2<=0; q<=0; end
    else begin m1<=d; m2<=m1; q<=m2; end
endmodule
module three_flop_per_bit (input logic bclk, brst_n, cclk, crst_n,
                   input logic [7:0] cfg_in, output logic [7:0] acc);
  logic [7:0] cfg_b, cfg_c;
  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) cfg_b <= 8'h00; else cfg_b <= cfg_in;
  genvar i;
  generate for (i=0;i<8;i++) begin : g
    sync3 u(cclk, crst_n, cfg_b[i], cfg_c[i]);
  end endgenerate
  always_ff @(posedge cclk or negedge crst_n)
    if (!crst_n) acc <= 8'h00; else acc <= acc + cfg_c;
endmodule
