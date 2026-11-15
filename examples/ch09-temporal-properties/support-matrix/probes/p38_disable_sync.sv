// Reset as an antecedent term in place of disable iff: a at t == 0, in
// reset, is not an attempt; a at t == 5 is, and b is absent there in the
// BAD instance (p38)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire rst_n = (t >= 4'd2);
  wire a = (t == 4'd0) || (t == 4'd5);
  wire b = (t == 4'd5) && !BAD;
  a1: assert property (@(posedge clk) (rst_n && a) |-> b)
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
      $display("PROBE p38 PASS");
    else
      $display(
        "PROBE p38 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
