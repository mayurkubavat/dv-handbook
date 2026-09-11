// Two one-bit chains carrying one two-bit value, with one sending flop
// behind a clock gate whose enable comes out of an adder -- something the
// netlist cannot see into, and which the evidence heuristic therefore
// scored as highly as the clock beside it. The two chains then reported
// different clock roots, the rule that groups parallel chains by boundary
// split them into two groups of one, and both came back as recognized
// synchronizers. The value leaves through the ports, so nothing inside
// reads the two chains together either.
module per_bit_mixed_roots (
    input  logic aclk,
    input  logic bclk,
    input  logic [3:0] x,
    input  logic [3:0] y,
    input  logic d0,
    input  logic d1,
    output logic o0,
    output logic o1
);
  logic [4:0] sum;
  logic g1, a0, a1, p0, p1, r0, r1;

  assign sum = x + y;
  assign g1  = aclk & sum[0];

  always_ff @(posedge aclk) a0 <= d0;
  always_ff @(posedge g1)   a1 <= d1;
  always_ff @(posedge bclk) begin p0 <= a0; p1 <= a1; end
  always_ff @(posedge bclk) begin r0 <= p0; r1 <= p1; end

  assign o0 = r0;
  assign o1 = r1;
endmodule
