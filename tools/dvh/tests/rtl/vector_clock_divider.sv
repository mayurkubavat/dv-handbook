// Two lanes, one clock each, on one vector port; a divider of lane 1's
// clock gates lane 0's. Clock dependencies compared by port *name* made a
// divider of `lane_clk[1]` a divider of the same clock as `lane_clk[0]`.
// They are compared by bit.
module vector_clock_divider (input logic [1:0] lane_clk, input logic [7:0] d,
               output logic [7:0] q);
  logic div1, gclk;
  logic [7:0] a, b;
  always_ff @(posedge lane_clk[1]) div1 <= ~div1;   // lane 1 divider
  assign gclk = lane_clk[0] & div1;                 // blend lane 0 with it
  always_ff @(posedge lane_clk[0]) a <= d;          // lane 0 domain
  always_ff @(posedge gclk) b <= a;                 // 8 bits, no sync
  assign q = b;
endmodule
