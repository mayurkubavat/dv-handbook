// clk2 is a clock that only ever appears blended, so it drives no clock
// pin directly and the completeness check cannot know it is a clock.
// `--clock clk1` alone is accepted, and clk2 is read as an enable. The
// tool cannot tell; what it can do is say which ports it read that way,
// and the report lists them.
module hidden_clock (input logic clk1, clk2, input logic [7:0] d,
               output logic [7:0] q);
  logic gclk;
  logic [7:0] a, b;
  always_ff @(posedge clk1) a <= d;
  assign gclk = clk1 & clk2;
  always_ff @(posedge gclk) b <= a;
  assign q = b;
endmodule
