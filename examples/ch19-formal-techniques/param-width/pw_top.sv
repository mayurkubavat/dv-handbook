// pw_top.sv -- the book's FIFO (Chapter 1's, or Chapter 9's repaired
// one: the script chooses the file) at a DEPTH the script chooses,
// with a ghost occupancy count built from the ports. The count is
// five bits wide, as Chapter 9's checker sizes its own, which is wide
// enough for DEPTH 16 and not for 32.
module pw_top #(parameter int DEPTH = 16) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic [4:0] occ;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) occ <= '0;
    else        occ <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
endmodule
