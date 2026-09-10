// two_clock_gates.sv -- one clock, two gates, no ungated register.
//
// Nothing here drives a clock pin straight from a port, so the walk has no
// strong evidence for which input of each gate is the clock. It says so
// rather than guessing, and the path between the two registers is reported
// as undecided: a person is asked to declare the clocks. Reporting it is
// the point. An earlier version decided the two domains shared a root and
// dropped the finding, which silenced real crossings elsewhere.
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
