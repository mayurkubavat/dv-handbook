// A named sequence with two arguments, instantiated in a consequent: a at
// t == 2, b at t == 3, absent in the BAD instance (p26)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = (t == 4'd3) && !BAD;
  sequence s(x, y);
    x ##1 y;
  endsequence
  a1: assert property (@(posedge clk) a |-> s(a, b)) else nf++;
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
      $display("PROBE p26 PASS");
    else
      $display(
        "PROBE p26 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
