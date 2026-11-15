// $assertoff and $asserton: ok is false at t == 3 and t == 8. Assertions
// are off from t == 2 to 5, so only the second is reported (p60)
module dut (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = (t != 4'd3) && (t != 4'd8);
  a1: assert property (@(posedge clk) ok) else nf++;
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut u (.clk);
  initial begin
    repeat (2) @(posedge clk);
    #1 $assertoff;
    repeat (4) @(posedge clk);
    #1 $asserton;
    repeat (8) @(posedge clk);
    #1;
    if (u.nf == 1)
      $display("PROBE p60 PASS");
    else
      $display("PROBE p60 FAIL failures=%0d, want 1", u.nf);
    $finish;
  end
endmodule
`endif
