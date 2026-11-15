// Vacuous success and the pass action block: in the good instance a never
// comes, so all 14 attempts succeed vacuously and the probe prints how
// often the pass statement ran. In the BAD instance a comes at t == 5
// without b: one failure (p53)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int np = 0;
  wire a = BAD && (t == 4'd5);
  wire b = 1'b0;
  a1: assert property (@(posedge clk) a |-> b) np++; else nf++;
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
      $display(
        "PROBE p53 PASS pass statement ran %0d times on 14 vacuous successes",
        good.np);
    else
      $display(
        "PROBE p53 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
