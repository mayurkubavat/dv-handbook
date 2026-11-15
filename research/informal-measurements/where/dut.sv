// Counter with properties written four ways.
module cnt_chk #(parameter int LIM = 9)
  (input logic clk, input logic rst, input logic [3:0] q);
  a_bound: assert property (@(posedge clk) disable iff (rst) q <= LIM);
endmodule
module cnt #(parameter int LIM = 9)
  (input logic clk, input logic rst, input logic en, output logic [3:0] q);
  always_ff @(posedge clk)
    if (rst) q <= '0;
    else if (en && q != LIM[3:0]) q <= q + 4'd1;
  // (1) concurrent SVA in the RTL
  a_rtl: assert property (@(posedge clk) disable iff (rst) q <= LIM);
  c_rtl: cover  property (@(posedge clk) q == LIM);
  // (2) immediate assertion in a clocked block
  always_ff @(posedge clk) if (!rst) a_imm: assert (q <= LIM);
  // (3) immediate assertion in combinational logic
  always_comb a_comb: assert (q != 4'd12);
`ifdef WITH_ACTION
  a_act: assert property (@(posedge clk) disable iff (rst) q <= LIM) else $error("q=%0d", q);
`endif
endmodule
module top(input logic clk, input logic rst, input logic en, output logic [3:0] q);
  cnt #(.LIM(9)) u_cnt(.*);
  // (4) checker module instantiated beside the DUT
  cnt_chk #(.LIM(9)) u_chk(.clk, .rst, .q);
endmodule
