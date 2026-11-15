// fifo_sva.sv -- the FIFO's plan items as properties, in a module that
// is bound to the design and drives nothing.
//
// Ports are inputs only. count is the design's own occupancy register,
// reached through the bind; the checker uses it in exactly one place,
// Sync_A, and judges the design by its own counter occ, which is built
// from the contract: a push is wr_en with !full, a pop is rd_en with
// !empty.
//
// Every property is a concurrent assertion in the chapter's subset: a
// clock, a reset that switches it off, and a boolean or an implication
// to this tick or the next. A simulator and a formal tool read the
// same text.
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
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      occ      <= '0;
      was_full <= 1'b0;
    end else begin
      occ      <= occ + 5'(wr_en && !full) - 5'(rd_en && !empty);
      was_full <= was_full || full;
    end

  // FIFO-010  occupancy never exceeds DEPTH
  NoOverflow_A:   assert property (@(posedge clk) disable iff (!rst_n)
                    occ <= 5'(DEPTH));
  // FIFO-005  full when all DEPTH entries are occupied, and only then
  FullForward_A:  assert property (@(posedge clk) disable iff (!rst_n)
                    occ == 5'(DEPTH) |-> full);
  FullBackward_A: assert property (@(posedge clk) disable iff (!rst_n)
                    full |-> occ == 5'(DEPTH));
  // FIFO-006  empty when no entries are occupied, and only then
  EmptyExact_A:   assert property (@(posedge clk) disable iff (!rst_n)
                    empty == (occ == 5'd0));
  // FIFO-007  a write while full is ignored: still full afterwards
  PushFull_A:     assert property (@(posedge clk) disable iff (!rst_n)
                    wr_en && full && !rd_en |=> full);
  // FIFO-008  a read while empty is ignored: still empty afterwards
  PopEmpty_A:     assert property (@(posedge clk) disable iff (!rst_n)
                    rd_en && empty && !wr_en |=> empty);
  // The checker's counter and the design's are the same number.
  Sync_A:         assert property (@(posedge clk) disable iff (!rst_n)
                    occ == count);

  // One cover per antecedent, reaching as far as its assertion does,
  // and one for each state the plan names.
  FullReached_C:  cover property (@(posedge clk) disable iff (!rst_n)
                    occ == 5'(DEPTH));
  PushFull_C:     cover property (@(posedge clk) disable iff (!rst_n)
                    wr_en && full && !rd_en ##1 1'b1);
  PopEmpty_C:     cover property (@(posedge clk) disable iff (!rst_n)
                    rd_en && empty && !wr_en ##1 1'b1);
  Drained_C:      cover property (@(posedge clk) disable iff (!rst_n)
                    was_full && empty);
endmodule
