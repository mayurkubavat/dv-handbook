// two_clock_gates.sv -- one clock, two gates, no ungated register.
//
// Nothing here drives a clock pin straight from a port, so the walk has no
// strong evidence for which input of each gate is the clock. Both resulting
// domains still share the root `clk`, so the path between them is the same
// clock gated two ways, not a crossing, and must not be reported as one.
module two_clock_gates (input logic clk, rst_n, en1, en2, d,
                output logic q1, q2);
  logic g1, g2;
  assign g1 = clk & en1;
  assign g2 = clk & en2;
  always_ff @(posedge g1 or negedge rst_n)
    if (!rst_n) q1 <= 1'b0; else q1 <= d;
  always_ff @(posedge g2 or negedge rst_n)
    if (!rst_n) q2 <= 1'b0; else q2 <= q1;
endmodule
