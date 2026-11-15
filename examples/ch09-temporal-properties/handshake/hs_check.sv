// hs_check.sv -- the valid/ready rule as clocked checks.
//
// Every check is an immediate assertion in a clocked block: a
// condition on the values of this tick and, through $past, of the tick
// before. A guard in front of the assertion says when the rule
// applies; a tick on which the guard is false checks nothing.
//
// past_ok is ordinary logic: high when the previous tick was out of
// reset, so that $past refers to a tick the rule may speak about.
module hs_check (
  input logic       clk,
  input logic       rst,
  input logic       valid,
  input logic       ready,
  input logic [7:0] data
);
  logic past_ok = 1'b0;
  always @(posedge clk) past_ok <= !rst;

  always @(posedge clk) begin
    // The same tick: ready is only ever an answer to an offer.
    if (!rst && ready)
      Answer_A:  assert (valid);
    // The next tick: an offer that was pending is still on the table,
    if (!rst && past_ok && $past(valid && !ready))
      Held_A:    assert (valid);
    // and it is the same offer.
    if (!rst && past_ok && $past(valid && !ready))
      Stable_A:  assert (data == $past(data));
    // Held_A with no reset term, to show what the term is for.
    if ($past(valid && !ready))
      HeldRaw_A: assert (valid);
    // The guard of the two rules above, as something to be seen.
    Waited_C: cover (!rst && past_ok && $past(valid && !ready));
  end
endmodule
