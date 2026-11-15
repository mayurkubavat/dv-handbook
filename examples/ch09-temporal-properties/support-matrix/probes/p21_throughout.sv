// throughout: a at t == 2, b at t == 4, en from 2 to 4, dropped at t == 3
// in the BAD instance (p21)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = (t == 4'd4);
  wire en = (t >= 4'd2) && (t <= 4'd4) && !(BAD && t == 4'd3);
  a1: assert property (@(posedge clk) a |-> en throughout (a ##2 b))
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
      $display("PROBE p21 PASS");
    else
      $display(
        "PROBE p21 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
