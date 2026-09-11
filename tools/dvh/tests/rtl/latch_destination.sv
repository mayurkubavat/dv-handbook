// The receiving element is a latch, not a flip-flop. The walks pass through
// a latch in the middle of a path and record it, which is right; a latch at
// the end of one was never asked about, because the loop that asks only
// visited flip-flops. Eight bits leave aclk into a transparent latch held
// open by a bclk enable: the enable edge can land anywhere in the data's
// transition, and the design reported as clean.
module latch_destination (
    input  logic aclk,
    input  logic bclk,
    input  logic [7:0] d,
    output logic [7:0] q,
    output logic ben
);
  logic [7:0] a;
  logic en;

  always_ff @(posedge aclk) a <= d;
  always_ff @(posedge bclk) en <= ^d;
  always_latch if (en) q <= a;

  assign ben = en;
endmodule
