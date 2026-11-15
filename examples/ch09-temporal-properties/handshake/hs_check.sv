// hs_check.sv -- the valid/ready rule as concurrent assertions.
//
// Each property names its clock, the reset that switches it off, and
// one implication: where the left side holds, the right side must
// hold on the same tick (|->) or on the next one (|=>). A tick on
// which the left side is false checks nothing.
module hs_check (
  input logic       clk,
  input logic       rst_n,
  input logic       valid,
  input logic       ready,
  input logic [7:0] data
);
  // The same tick: ready is only ever an answer to an offer.
  Answer_A:  assert property (@(posedge clk) disable iff (!rst_n)
               ready |-> valid);
  // The next tick: an offer that is pending is still on the table,
  Held_A:    assert property (@(posedge clk) disable iff (!rst_n)
               valid && !ready |=> valid);
  // and it is the same offer.
  Stable_A:  assert property (@(posedge clk) disable iff (!rst_n)
               valid && !ready |=> $stable(data));
  // Held_A with no reset term, to show what the term is for.
  HeldRaw_A: assert property (@(posedge clk)
               valid && !ready |=> valid);
  // The left side of the two rules above, and the tick on which their
  // right side is judged, as something to be seen.
  Waited_C:  cover property (@(posedge clk) disable iff (!rst_n)
               valid && !ready ##1 1'b1);
endmodule
