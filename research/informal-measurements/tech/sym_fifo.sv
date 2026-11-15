// Symbolic constant + one tracked word (data independence) on the fixed FIFO
module sym_fifo (
  input logic clk, rst_n, wr_en, rd_en, pick,
  input logic [7:0] wr_data,
  input logic [7:0] sd,          // symbolic constant: free, assumed stable
  output logic [7:0] rd_data, output logic full, empty
);
  fifo u (.*);
  logic in_q; logic [4:0] ahead;
  wire take = pick && u.do_write && wr_data == sd && !in_q;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin in_q <= 1'b0; ahead <= '0; end
    else if (take) begin in_q <= 1'b1; ahead <= u.count - u.do_read; end
    else if (in_q && u.do_read) begin
      if (ahead == 0) in_q <= 1'b0; else ahead <= ahead - 5'd1;
    end
endmodule
