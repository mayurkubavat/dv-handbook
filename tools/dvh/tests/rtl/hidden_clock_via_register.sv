// A clock that only ever appears gated, reaching the gate through a
// register in its own domain. The completeness check cannot know it is a
// clock, and no *port* is demoted at the gate -- the register is. So a
// demoted register is reported by the ports that clock it, and the report
// names the hidden clock.
module hidden_clock_via_register (input logic clk1, hclk, en,
                                  input logic [7:0] d,
               output logic [7:0] q);
  logic hg, r, gclk;
  logic [7:0] a, b;
  assign hg = hclk & en;
  always_ff @(posedge hg) r <= ~r;         // register in the hidden domain
  assign gclk = clk1 & r;                  // blend
  always_ff @(posedge clk1) a <= d;
  always_ff @(posedge gclk) b <= a;        // 8 bits, no synchronizer
  assign q = b;
endmodule
