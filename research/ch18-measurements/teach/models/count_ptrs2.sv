module count_ptrs (input logic clk, input logic rst_n, input logic wr_en, input logic rd_en);
  logic full, empty, rd_data;
  fifo #(.WIDTH(1), .DEPTH(2)) dut (.wr_data(1'b0), .*);
  logic started = 1'b0;
  always_ff @(posedge clk) started <= 1'b1;
  always_comb begin
    Reset_M:     assume (rst_n == started);
    CountPtrs_A: assert (!rst_n || dut.count[0:0] == dut.wr_ptr - dut.rd_ptr);
  end
endmodule
