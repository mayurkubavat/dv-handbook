// The same model with the properties as concurrent assertions (clocked
// booleans), bound into fifo.
module fifo_props #(parameter int DEPTH = 16) (
  input logic clk, input logic rst_n,
  input logic wr_en, input logic rd_en, input logic full, input logic empty,
  input logic [4:0] count);
  logic [4:0] occ;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) occ <= '0;
    else        occ <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
  NoOverflow_A:   assert property (@(posedge clk) disable iff (!rst_n) occ <= 5'(DEPTH));
  FullForward_A:  assert property (@(posedge clk) disable iff (!rst_n) occ == 5'(DEPTH) |-> full);
  FullBackward_A: assert property (@(posedge clk) disable iff (!rst_n) full |-> occ == 5'(DEPTH));
  EmptyExact_A:   assert property (@(posedge clk) disable iff (!rst_n) empty == (occ == 5'd0));
  FullReached_C:  cover  property (@(posedge clk) disable iff (!rst_n) occ == 5'(DEPTH));
`ifdef HELPER
  Sync_A:         assert property (@(posedge clk) disable iff (!rst_n) occ == count);
`endif
endmodule
bind fifo fifo_props #(.DEPTH(DEPTH)) u_props (.clk, .rst_n, .wr_en, .rd_en, .full, .empty, .count(5'(count)));
