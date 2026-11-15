// A two-clock property: a at t == 2 on clk, then b at the next edge of
// clk2; b is low throughout in the BAD instance (p59)
module dut #(parameter bit BAD = 0) (input logic clk, input logic clk2);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = !BAD;
  a1: assert property (@(posedge clk) a |=> @(posedge clk2) b)
    else nf++;
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  bit clk2;
  always #7 clk2 = ~clk2;
  dut #(.BAD(0)) good (.clk, .clk2);
  dut #(.BAD(1)) bad (.clk, .clk2);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (good.nf == 0 && bad.nf == 1)
      $display("PROBE p59 PASS");
    else
      $display(
        "PROBE p59 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
