// sc_free.sv -- the same symbolic slot address as sc_any.sv, as a
// free input that the script holds constant with an assumption: the
// spelling this tool takes. A push to the slot sa leaves the pushed
// word there. The module also records sa in the previous cycle, and
// marks the first cycle after reset, for the question of what a
// $stable assumption says about the reset cycle.
module sc_free #(parameter int DEPTH = 16) (
  input  logic                     clk, rst_n, wr_en, rd_en,
  input  logic [7:0]               wr_data,
  input  logic [$clog2(DEPTH)-1:0] sa,
  output logic [7:0]               rd_data,
  output logic                     full, empty
);
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic [$clog2(DEPTH)-1:0] sa0;              // sa in the previous cycle
  logic                     first;            // the cycle after reset
  always_ff @(posedge clk) sa0 <= sa;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) first <= 1'b1;
    else        first <= 1'b0;
  Slot_A: assert property (@(posedge clk) disable iff (!rst_n)
            u.do_write && u.wr_ptr == sa |=> u.mem[sa] == $past(wr_data));
endmodule
