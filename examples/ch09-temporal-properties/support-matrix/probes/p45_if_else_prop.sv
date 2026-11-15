// Property if/else: x must hold on odd t and y on even t. In the BAD
// instance x is missing at t == 5 and y at t == 6, one failure in each
// branch (p45)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire m = t[0];
  wire x = t[0] && !(BAD && t == 4'd5);
  wire y = !t[0] && !(BAD && t == 4'd6);
  a1: assert property (@(posedge clk) if (m) x else y) else nf++;
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
    if (good.nf == 0 && bad.nf == 2)
      $display("PROBE p45 PASS");
    else
      $display(
        "PROBE p45 FAIL failures good=%0d bad=%0d, want 0 and 2",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
