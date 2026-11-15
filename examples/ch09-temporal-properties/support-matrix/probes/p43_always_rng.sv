// always [2:5]: started at t == 1, so a must hold from t == 3 to 6; it
// drops at t == 5 in the BAD instance (p43)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire go = (t == 4'd1);
  wire a = (t >= 4'd3) && (t <= 4'd6) && !(BAD && t == 4'd5);
  a1: assert property (@(posedge clk) go |-> always [2:5] a)
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
    if (good.nf == 0 && bad.nf == 1)
      $display("PROBE p43 PASS");
    else
      $display(
        "PROBE p43 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
