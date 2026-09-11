// A clock blended with a *divided* clock. The evidence heuristic counted a
// divider as a clock only if its own output drove a clock pin with nothing
// in between -- which is every divider except the ones that matter here --
// so this one scored as gating control and the crossing was excused from
// the gate. Declaring the clocks replaces the evidence with a definition: a
// register clocked by a clock is itself a clock, to any depth.
module divided_blend (
    input  logic clk1,
    input  logic clk2,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic clk2div, gclk;
  logic [7:0] a, b;

  always_ff @(posedge clk2) clk2div <= ~clk2div;
  assign gclk = clk1 & clk2div;

  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;     // eight bits, no synchronizer

  assign q = b;
endmodule
