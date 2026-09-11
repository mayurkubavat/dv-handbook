// A submodule marked `keep_hierarchy`, which is the ordinary way to stop a
// synthesis flow dissolving a block -- and is applied most often to exactly
// the blocks a crossing report cares about. Yosys honors the attribute, so
// `flatten` left the instance alone and every register in the design was in
// a module the walks never looked at: no clocks, no registers, no
// crossings, and the build passed on a design that contains all three.
(* keep_hierarchy *)
module kept_hierarchy_lane (
    input  logic aclk,
    input  logic bclk,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic [7:0] a, b;

  always_ff @(posedge aclk) a <= d;
  always_ff @(posedge bclk) b <= a;     // eight bits, no synchronizer

  assign q = b;
endmodule

module kept_hierarchy (
    input  logic aclk,
    input  logic bclk,
    input  logic [7:0] d,
    output logic [7:0] q
);
  kept_hierarchy_lane u_lane (.aclk(aclk), .bclk(bclk), .d(d), .q(q));
endmodule
