// Plassan's *blending*: two clocks combined to make a third. `clk2` is an
// independent asynchronous clock, not an enable, and it drives no
// register's clock pin directly -- so the walk has no strong evidence for
// it and once demoted it to gating control, silently. Both registers then
// reported the same clock root, the crossing was excused as "one clock,
// gated differently", and the build passed on an eight-bit unsynchronized
// path between two unrelated clocks.
//
// Nothing in the netlist separates this from a clock gate. The walk now
// says so, and `--clock` is how a specification settles it.
module blended_clock (
    input  logic clk1,
    input  logic clk2,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic gclk;
  logic [7:0] a, b;

  assign gclk = clk1 & clk2;

  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;     // eight bits, no synchronizer

  assign q = b;
endmodule
