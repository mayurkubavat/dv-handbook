// split_source_sync.sv -- the per-bit anti-pattern with no shared name.
//
// Eight separately declared flops carry one value across, one synchronizer
// each, and a downstream register reads them together. Grouping by the
// sending register's name would miss this entirely; what gives it away is
// that something downstream reads the eight outputs as one value.
module sync1s (input logic clk, rst_n, d, output logic q);
  logic meta;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin meta <= 1'b0; q <= 1'b0; end
    else        begin meta <= d;    q <= meta; end
endmodule
module split_source_sync (input logic bclk, brst_n, cclk, crst_n,
                 input logic [7:0] cfg_in, output logic [7:0] acc);
  logic s0,s1,s2,s3,s4,s5,s6,s7;
  logic [7:0] cfg_c;
  always_ff @(posedge bclk or negedge brst_n)
    if (!brst_n) begin s0<=0;s1<=0;s2<=0;s3<=0;s4<=0;s5<=0;s6<=0;s7<=0; end
    else begin s0<=cfg_in[0];s1<=cfg_in[1];s2<=cfg_in[2];s3<=cfg_in[3];
               s4<=cfg_in[4];s5<=cfg_in[5];s6<=cfg_in[6];s7<=cfg_in[7]; end
  sync1s u0(cclk,crst_n,s0,cfg_c[0]); sync1s u1(cclk,crst_n,s1,cfg_c[1]);
  sync1s u2(cclk,crst_n,s2,cfg_c[2]); sync1s u3(cclk,crst_n,s3,cfg_c[3]);
  sync1s u4(cclk,crst_n,s4,cfg_c[4]); sync1s u5(cclk,crst_n,s5,cfg_c[5]);
  sync1s u6(cclk,crst_n,s6,cfg_c[6]); sync1s u7(cclk,crst_n,s7,cfg_c[7]);
  always_ff @(posedge cclk or negedge crst_n)
    if (!crst_n) acc <= 8'h00; else acc <= acc + cfg_c;
endmodule
