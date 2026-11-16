// iv.sv -- the book's FIFO with a flag that is true in the first
// cycle only. With the shell's reset turned off, every register
// starts free; an assumption on `first` then picks the start states.
module iv_top #(parameter int DEPTH = 256) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic first;
  initial first = 1'b1;
  always @(posedge clk) first <= 1'b0;
endmodule
