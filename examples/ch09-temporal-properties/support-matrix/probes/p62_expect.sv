// expect: a procedural statement that blocks until its property is
// decided. Started at time zero, it sees a at t == 0 and needs b at t ==
// 1, absent in the BAD instance (p62)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd0);
  wire b = (t == 4'd1) && !BAD;
  initial expect (@(posedge clk) a ##1 b) else nf++;
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
      $display("PROBE p62 PASS");
    else
      $display(
        "PROBE p62 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
