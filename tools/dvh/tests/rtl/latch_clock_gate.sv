// The clock gate @sec-ch03-clocks describes: a latch holds the enable while
// the clock is high so the gate cannot glitch. One clock, gated; every
// crossing here is synchronous, and with the clock declared the design
// passes. A latch is state, so the walk treats its output like a
// register's rather than passing straight through it.
module latch_clock_gate (input logic clk, en, input logic [7:0] d,
                         output logic [7:0] q);
  logic en_l, gclk;
  logic [7:0] a, b;
  always_latch if (~clk) en_l <= en;   // enable latch, transparent low
  assign gclk = clk & en_l;
  always_ff @(posedge clk)  a <= d;
  always_ff @(posedge gclk) b <= a;    // same clock, gated
  assign q = b;
endmodule
