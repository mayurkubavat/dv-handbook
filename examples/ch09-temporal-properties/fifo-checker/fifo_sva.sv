// fifo_sva.sv -- the FIFO's plan items as checks, in a module that is
// bound to the design and drives nothing.
//
// Ports are inputs only. count is the design's own occupancy register,
// reached through the bind; the checker uses it in exactly one place,
// the helper Sync_A, and judges the design by its own counter occ,
// which is built from the contract: a push is wr_en with !full, a pop
// is rd_en with !empty.
//
// Every check is an immediate assertion in a clocked block, guarded by
// reset: a condition on this tick and, through $past, the one before.
module fifo_sva #(parameter int DEPTH = 16) (
  input logic       clk,
  input logic       rst_n,
  input logic       wr_en,
  input logic       rd_en,
  input logic       full,
  input logic       empty,
  input logic [4:0] count
);
  // ---- monitor state, as ordinary registers -------------------------
  logic [4:0] occ;                 // occupancy by the contract
  logic       was_full;            // full has been seen since reset
  logic       past_ok;             // the tick before was out of reset
  always @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      occ      <= '0;
      was_full <= 1'b0;
      past_ok  <= 1'b0;
    end else begin
      occ      <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
      was_full <= was_full || full;
      past_ok  <= 1'b1;
    end

  always @(posedge clk) if (rst_n) begin
    // FIFO-010  occupancy never exceeds DEPTH
    NoOverflow_A:   assert (occ <= 5'(DEPTH));
    // FIFO-005  full when all DEPTH entries are occupied, and only then
    FullForward_A:  assert (!(occ == 5'(DEPTH)) || full);
    FullBackward_A: assert (!full || occ == 5'(DEPTH));
    // FIFO-006  empty when no entries are occupied, and only then
    EmptyExact_A:   assert (empty == (occ == 5'd0));
    // FIFO-007  a write while full is ignored: still full afterwards
    if (past_ok && $past(wr_en && full && !rd_en))
      PushFull_A:   assert (full);
    // FIFO-008  a read while empty is ignored: still empty afterwards
    if (past_ok && $past(rd_en && empty && !wr_en))
      PopEmpty_A:   assert (empty);
    // The checker's counter and the design's are the same number.
    Sync_A:         assert (occ == count);

    // One cover per guard, and one for each state the plan names.
    FullReached_C:  cover (occ == 5'(DEPTH));
    PushFull_C:     cover (past_ok && $past(wr_en && full && !rd_en));
    PopEmpty_C:     cover (past_ok && $past(rd_en && empty && !wr_en));
    Drained_C:      cover (was_full && empty);
  end
endmodule
