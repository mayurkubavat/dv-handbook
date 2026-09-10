// latch_enable_crossing.sv -- a crossing that arrives on a latch's enable.
//
// The walk was changed once already to pass through a latch rather than
// stop at one, because stopping hid the crossing behind it. It passed
// through the data input only, so a register in one domain driving the
// *enable*, with the latch's output sampled in another, reported nothing.
module latch_enable_crossing (
  input  logic aclk, bclk, rst_n, d, dat,
  output logic q
);
  logic en_a, lat;
  always_ff @(posedge aclk or negedge rst_n)
    if (!rst_n) en_a <= 1'b0; else en_a <= d;
  always_latch if (en_a) lat = dat;
  always_ff @(posedge bclk or negedge rst_n)
    if (!rst_n) q <= 1'b0; else q <= lat;
endmodule
