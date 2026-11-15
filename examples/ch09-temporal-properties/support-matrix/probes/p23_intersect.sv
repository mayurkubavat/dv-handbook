// intersect: b at t == 2 and c at t == 4 fix the length at three ticks, so
// a must hold from 2 to 4; it drops at t == 4 in the BAD instance (p23)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire b = (t == 4'd2);
  wire c = (t == 4'd4);
  wire a = (t >= 4'd2) && (t <= 4'd4) && !(BAD && t == 4'd4);
  a1: assert property (@(posedge clk)
    b |-> a[*1:3] intersect (b ##2 c)) else nf++;
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
      $display("PROBE p23 PASS");
    else
      $display(
        "PROBE p23 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
