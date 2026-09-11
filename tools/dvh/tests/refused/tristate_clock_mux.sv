// A clock multiplexer written as two tri-state drivers on one net. The
// netlist reader kept whichever driver came last, so one of the two
// clocks vanished before any walk began and the crossing onto the
// selected clock was excused. A net with more than one driver is now
// refused: this design is not analyzed, and the report says so with
// exit 2 rather than exit 0.
module tristate_clock_mux (input logic clk1, clk2, sel, input logic [7:0] d,
               output logic [7:0] q, output logic t);
  wire mclk;
  logic tog;
  logic [7:0] a, b;
  assign mclk = sel ? clk2 : 1'bz;
  assign mclk = sel ? 1'bz : clk1;
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge mclk) b <= a;
  always_ff @(posedge clk2) tog <= ~tog;
  assign q = b;
  assign t = tog;
endmodule
