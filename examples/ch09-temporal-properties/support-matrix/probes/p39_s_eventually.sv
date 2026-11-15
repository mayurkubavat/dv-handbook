// s_eventually: a at t == 2, b at t == 5, never in the BAD instance, where
// a strong obligation is still pending when the run ends. The probe
// requires no failure in the good instance and more passes there than in
// the bad one, and prints whether the pending obligation was reported
// before $finish (p39)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int np = 0;
  wire a = (t == 4'd2);
  wire b = (t == 4'd5) && !BAD;
  a1: assert property (@(posedge clk) a |-> s_eventually b) np++;
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
        "PROBE p39 PASS b never comes: %0d failures reported",
        bad.nf);
    else
      $display(
        "PROBE p39 FAIL pass/fail good=%0d/%0d bad=%0d/%0d",
        good.np, good.nf, bad.np, bad.nf);
    $finish;
  end
endmodule
`endif
