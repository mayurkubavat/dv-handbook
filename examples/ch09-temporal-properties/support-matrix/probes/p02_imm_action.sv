// Immediate assertion with both action blocks, written without any macro
// so that every front end sees them: 14 ticks, so 14 passes in the good
// instance, 13 and one failure in the bad one (p02)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int np = 0;
  wire ok = !(BAD && t == 4'd5);
  always @(posedge clk) a1: assert (ok) np++; else nf++;
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
    if (good.np == 14 && good.nf == 0 && bad.np == 13 && bad.nf == 1)
      $display("PROBE p02 PASS");
    else
      $display(
        "PROBE p02 FAIL pass/fail good=%0d/%0d bad=%0d/%0d, want 14/0 and 13/1",
        good.np, good.nf, bad.np, bad.nf);
    $finish;
  end
endmodule
`endif
