// cover property of a sequence, counted by its pass statement: a at t ==
// 2, b at t == 3, so one hit; b is absent in the BAD instance, so none
// (p49)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int nc = 0;
  wire a = (t == 4'd2);
  wire b = (t == 4'd3) && !BAD;
  c1: cover property (@(posedge clk) a ##1 b) nc++;
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
    if (good.nc == 1 && bad.nc == 0)
      $display("PROBE p49 PASS");
    else
      $display(
        "PROBE p49 FAIL hits good=%0d bad=%0d, want 1 and 0",
        good.nc, bad.nc);
    $finish;
  end
endmodule
`endif
