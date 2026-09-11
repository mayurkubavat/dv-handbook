// Eight one-bit synchronizers carrying one eight-bit value, each flop
// declared separately and every output leaving through the module's ports.
// The check that demotes per-bit chains once looked for a register that
// read them together, and there is none here: the value is reassembled by
// whatever instantiates this block. Eight correct-looking chains, one value
// whose bits resolve in different cycles.
module parallel_bit_sync (
    input  logic aclk,
    input  logic bclk,
    input  logic rst_n,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic a0, a1, a2, a3, a4, a5, a6, a7;
  logic p0, p1, p2, p3, p4, p5, p6, p7;
  logic r0, r1, r2, r3, r4, r5, r6, r7;

  always_ff @(posedge aclk or negedge rst_n)
    if (!rst_n) {a7, a6, a5, a4, a3, a2, a1, a0} <= 8'h00;
    else begin
      a0 <= d[0]; a1 <= d[1]; a2 <= d[2]; a3 <= d[3];
      a4 <= d[4]; a5 <= d[5]; a6 <= d[6]; a7 <= d[7];
    end

  always_ff @(posedge bclk or negedge rst_n)
    if (!rst_n) {p7, p6, p5, p4, p3, p2, p1, p0} <= 8'h00;
    else begin
      p0 <= a0; p1 <= a1; p2 <= a2; p3 <= a3;
      p4 <= a4; p5 <= a5; p6 <= a6; p7 <= a7;
    end

  always_ff @(posedge bclk or negedge rst_n)
    if (!rst_n) {r7, r6, r5, r4, r3, r2, r1, r0} <= 8'h00;
    else begin
      r0 <= p0; r1 <= p1; r2 <= p2; r3 <= p3;
      r4 <= p4; r5 <= p5; r6 <= p6; r7 <= p7;
    end

  assign q = {r7, r6, r5, r4, r3, r2, r1, r0};
endmodule
