// ##[1:$] is weak: a at t == 2, b at t == 5, never in the BAD instance,
// where the attempt is still pending when the run ends. No failure is
// required of either; that the assertion is alive shows in the pass count,
// one higher where b came (p14)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int np = 0;
  wire a = (t == 4'd2);
  wire b = (t == 4'd5) && !BAD;
  a1: assert property (@(posedge clk) a |-> ##[1:$] b) np++;
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
    if (good.nf == 0 && good.np > bad.np)
      $display(
        "PROBE p14 PASS b never comes: %0d failures reported",
        bad.nf);
    else
      $display(
        "PROBE p14 FAIL pass/fail good=%0d/%0d bad=%0d/%0d",
        good.np, good.nf, bad.np, bad.nf);
    $finish;
  end
endmodule
`endif
