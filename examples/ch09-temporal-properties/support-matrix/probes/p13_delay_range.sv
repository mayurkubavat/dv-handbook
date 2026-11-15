// ##[1:3]: a at t == 1, 2 and 5, the first two overlapping. b at t == 4
// serves both of those; b at t == 8 serves the third, and in the BAD
// instance it comes at t == 9, one tick late (p13)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd1) || (t == 4'd2) || (t == 4'd5);
  wire b = (t == 4'd4) || (t == (BAD ? 4'd9 : 4'd8));
  a1: assert property (@(posedge clk) a |-> ##[1:3] b) else nf++;
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
      $display("PROBE p13 PASS");
    else
      $display(
        "PROBE p13 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
