// shared_enable_clocks.sv -- two asynchronous clocks, one global enable.
//
// aclk and bclk are unrelated, and both are gated by the same `run`. With
// no ungated register the walk cannot tell clock from enable, so the
// enable lands in both domain names. An earlier version suppressed any
// crossing whose domain names shared a token, and silenced this one: a
// real unsynchronized crossing reported as a clean design, exit 0, on a
// shape as ordinary as a global clock enable.
module shared_enable_clocks (
  input  logic aclk, bclk, rst_n, run, d,
  output logic q
);
  logic ga, gb, a;
  assign ga = aclk & run;
  assign gb = bclk & run;
  always_ff @(posedge ga or negedge rst_n)
    if (!rst_n) a <= 1'b0; else a <= d;
  always_ff @(posedge gb or negedge rst_n)
    if (!rst_n) q <= 1'b0; else q <= a;
endmodule
