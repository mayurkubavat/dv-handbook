// A property-local variable: at each v the data d is captured and compared
// with q three ticks later. v at t == 2, 3 and 6, so two attempts overlap
// and each needs its own copy. q is d delayed by three, except at t == 9
// in the BAD instance (p28)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire v = (t == 4'd2) || (t == 4'd3) || (t == 4'd6);
  wire [3:0] d = t;
  wire [3:0] q = t - 4'd3 + {3'd0, BAD && t == 4'd9};
  property p;
    logic [3:0] x;
    @(posedge clk) (v, x = d) |-> ##3 (q == x);
  endproperty
  a1: assert property (p) else nf++;
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut #(.BAD(0)) good (.clk);
  dut #(.BAD(1)) bad (.clk);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (good.nf == 0 && bad.nf == 1)
      $display("PROBE p28 PASS");
    else
      $display(
        "PROBE p28 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
