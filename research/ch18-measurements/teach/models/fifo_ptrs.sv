// fifo_ptrs.sv -- the repaired FIFO at DEPTH 4 with a reset cycle
// written as hardware, and one property of its own registers.
module fifo_ptrs (
  input logic clk,
  input logic rst_n,
  input logic wr_en,
  input logic rd_en
);
  logic full, empty, rd_data;
  fifo #(.WIDTH(1), .DEPTH(4)) dut (.wr_data(1'b0), .*);

  logic started = 1'b0;             // 0 in the first cycle only
  always_ff @(posedge clk) started <= 1'b1;

  always_comb begin
    Reset_M:     assume (rst_n == started);
    EmptyPtrs_A: assert (!rst_n || !empty || dut.wr_ptr == dut.rd_ptr);
`ifdef HELPER
    CountPtrs_M: assume (!rst_n || dut.count[1:0] == dut.wr_ptr - dut.rd_ptr);
`endif
  end
endmodule
