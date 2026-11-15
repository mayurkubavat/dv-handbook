// A sequence with a fixed delay as antecedent, the contrast to x12: a at t
// == 2, b at t == 4, c due at t == 4; absent in the BAD instance (x13)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = (t == 4'd4);
  wire c = (t == 4'd4) && !BAD;
  a1: assert property (@(posedge clk) (a ##2 b) |-> c) else nf++;
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
      $display("PROBE x13 PASS");
    else
      $display(
        "PROBE x13 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
