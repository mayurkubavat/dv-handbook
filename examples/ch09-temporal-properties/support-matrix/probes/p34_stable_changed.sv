// $stable and $changed: x changes once, at t == 4. The BAD instance
// expects the change at t == 5, so each assertion fails at t == 4 and at t
// == 5 (p34)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire x = (t >= 4'd4);
  wire e = (t == (BAD ? 4'd5 : 4'd4));
  wire g = (t == 4'd0);          // the first tick is p30's
  a1: assert property (@(posedge clk) g || ($changed(x) == e))
    else nf++;
  a2: assert property (@(posedge clk) g || ($stable(x) == !e))
    else nf++;
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
    if (good.nf == 0 && bad.nf == 4)
      $display("PROBE p34 PASS");
    else
      $display(
        "PROBE p34 FAIL failures good=%0d bad=%0d, want 0 and 4",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
