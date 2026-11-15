// disable iff: ok is false at t == 0, inside reset (t < 2), which must not
// be reported, and at t == 5 in the BAD instance, which must (p07)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire rst_n = (t >= 4'd2);
  wire ok = (t != 4'd0) && !(BAD && t == 4'd5);
  a1: assert property (@(posedge clk) disable iff (!rst_n) ok)
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
      $display("PROBE p07 PASS");
    else
      $display(
        "PROBE p07 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
