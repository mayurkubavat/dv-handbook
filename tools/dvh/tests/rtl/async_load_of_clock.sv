// A register whose asynchronous load *value* is the other clock: while
// the load is high its output follows clk2. Two lists of what a register
// depends on -- first its clock, then its clock and asynchronous controls
// -- each missed the next pin a design used; the walk now follows every
// input a register does not sample on its clock, which is a list of what
// is excluded.
module async_load_of_clock (input logic clk1, clk2, ld, input logic [7:0] d,
                output logic [7:0] q, output logic t);
  logic flag, gclk, tog;
  logic [7:0] a, b;
  always_ff @(posedge clk1 or posedge ld)
    if (ld) flag <= clk2; else flag <= 1'b0;
  assign gclk = clk1 & flag;
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;
  always_ff @(posedge clk2) tog <= ~tog;
  assign q = b;
  assign t = tog;
endmodule
