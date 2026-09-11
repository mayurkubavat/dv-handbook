// Two bits of one value crossing on two one-bit synchronizers, with the two
// sending flops behind two different clock gates off one clock. The rule
// that demotes parallel chains grouped them by *domain key*, and one clock
// gated two ways is two domain keys -- so two chains off one physical clock
// were two groups of one and neither rule fired. `keep` is an ungated
// register on aclk, which gives the walk strong evidence for aclk so the
// gates resolve rather than being reported as undecided.
module per_bit_behind_gates (
    input  logic aclk,
    input  logic bclk,
    input  logic en0,
    input  logic en1,
    input  logic d0,
    input  logic d1,
    output logic [1:0] q,
    output logic k
);
  logic g0, g1, keep, a0, a1, p0, p1, r0, r1;

  assign g0 = aclk & en0;
  assign g1 = aclk & en1;

  always_ff @(posedge aclk) keep <= d0;
  always_ff @(posedge g0)   a0 <= d0;
  always_ff @(posedge g1)   a1 <= d1;
  always_ff @(posedge bclk) p0 <= a0;   // first stages
  always_ff @(posedge bclk) p1 <= a1;
  always_ff @(posedge bclk) r0 <= p0;   // second stages
  always_ff @(posedge bclk) r1 <= p1;

  assign q = {r1, r0};
  assign k = keep;
endmodule
