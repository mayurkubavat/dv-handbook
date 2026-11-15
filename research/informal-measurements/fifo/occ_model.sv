// Occupancy model only: state, no properties. Bound into fifo so that
// properties given by Tcl command can name u_occ.occ.
module occ_model (
  input logic clk, input logic rst_n,
  input logic wr_en, input logic rd_en, input logic full, input logic empty);
  logic [4:0] occ;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) occ <= '0;
    else        occ <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
endmodule
bind fifo occ_model u_occ (.clk, .rst_n, .wr_en, .rd_en, .full, .empty);
