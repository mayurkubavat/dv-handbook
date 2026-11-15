// fifo_bmc.sv -- the first chapter's FIFO with everything a model
// checker needs written out as hardware: a reset sequence, an
// occupancy counter built from the contract, and one assertion.
module fifo_bmc (
  input logic       clk,
  input logic       rst_n,
  input logic       wr_en,
  input logic [7:0] wr_data,
  input logic       rd_en
);
  logic [7:0] rd_data;
  logic       full, empty;
  fifo dut (.*);

  logic       started = 1'b0;       // 0 in the first cycle only
  logic [4:0] occ;                  // occupancy by the contract
  always_ff @(posedge clk) begin
    started <= 1'b1;
    if (!rst_n) occ <= '0;
    else        occ <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
  end

  always_comb begin
    // Reset is held for the first cycle and released for good.
    Reset_M:        assume (rst_n == started);
    // "full only when sixteen entries are occupied": the direction
    // of the specification's sentence that the first chapter's bug
    // breaks.
    FullBackward_A: assert (!rst_n || !full || occ == 5'd16);
  end
endmodule
