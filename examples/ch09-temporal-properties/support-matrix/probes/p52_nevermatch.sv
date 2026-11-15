// An antecedent that cannot match: the two operands of intersect have
// different lengths. The consequent is false, so any match would fail;
// none may be reported in either instance, and the runner records whether
// the tool warned (p52)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = 1'b1;
  wire e = 1'b0;
  a1: assert property (@(posedge clk)
    (a ##1 a) intersect (a ##2 a) |-> e) else nf++;
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
    if (good.nf == 0 && bad.nf == 0)
      $display("PROBE p52 PASS");
    else
      $display(
        "PROBE p52 FAIL failures good=%0d bad=%0d, want 0 and 0",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
