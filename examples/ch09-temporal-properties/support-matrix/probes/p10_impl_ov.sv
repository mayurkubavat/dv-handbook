// a |-> b: a at t == 3 and t == 6; b accompanies both, except at t == 6 in
// the BAD instance (p10)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd3) || (t == 4'd6);
  wire b = (t == 4'd3) || (t == 4'd6 && !BAD);
  a1: assert property (@(posedge clk) a |-> b) else nf++;
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
      $display("PROBE p10 PASS");
    else
      $display(
        "PROBE p10 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
