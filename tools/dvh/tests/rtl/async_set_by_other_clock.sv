// A flag set asynchronously by one clock's edge and cleared on another,
// used to gate the second. A register's output depends on its clock *and*
// on every pin that changes it at its own edge; following the clock alone
// made this flag control, and the blend one clock gated.
module async_set_by_other_clock (input logic clk1, clk2, input logic [7:0] d,
                 output logic [7:0] q, output logic t);
  logic flag, gclk, tog;
  logic [7:0] a, b;
  always_ff @(posedge clk1 or posedge clk2)
    if (clk2) flag <= 1'b1; else flag <= 1'b0;   // rises with clk2
  assign gclk = clk1 & flag;
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;              // 8 bits, no synchronizer
  always_ff @(posedge clk2) tog <= ~tog;
  assign q = b;
  assign t = tog;
endmodule
