// $past(t, 3) equals t - 3 from the fourth tick on; the BAD instance
// expects a wrong value at t == 6 (p31)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire [3:0] prev3 = t - 4'd3 - {3'd0, BAD && t == 4'd6};
  a1: assert property (@(posedge clk)
    (t < 4'd3) || ($past(t, 3) == prev3)) else nf++;
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
      $display("PROBE p31 PASS");
    else
      $display(
        "PROBE p31 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
