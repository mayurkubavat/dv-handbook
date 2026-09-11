// A glitch-free clock multiplexer, written the way one is actually written:
// out of gates, not out of a ternary. The walk grew a rule that a
// multiplexer never demotes an input, because selecting between two clocks
// is not gating -- and that rule keyed on the netlist's `$mux` cell, which
// this design never produces.
module gate_built_clock_mux (
    input  logic clk1,
    input  logic clk2,
    input  logic sel,
    input  logic [7:0] d,
    output logic [7:0] q
);
  logic cout;
  logic [7:0] a, b;

  assign cout = (clk1 & ~sel) | (clk2 & sel);

  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge cout) b <= a;     // eight bits, no synchronizer

  assign q = b;
endmodule
