// `keep_hierarchy` on the *instance* rather than the module, which is the
// ordinary way to keep one block out of a flatten. Stripping only the
// module form of the attribute left the instance standing, and the check
// that notices an unflattened design then turned the whole analysis off.
module kept_instance_lane (
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

module kept_instance (
    input  logic aclk,
    input  logic bclk,
    input  logic [7:0] d,
    output logic [7:0] q
);
  (* keep_hierarchy *)
  kept_instance_lane u_lane (.aclk(aclk), .bclk(bclk), .d(d), .q(q));
endmodule
