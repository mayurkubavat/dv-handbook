// a[*3]: from t == 2 a holds for three ticks, two in the BAD instance
// (p15)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire go = (t == 4'd2);
  wire a = (t >= 4'd2) && (t <= (BAD ? 4'd3 : 4'd4));
  a1: assert property (@(posedge clk) go |-> a[*3]) else nf++;
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
      $display("PROBE p15 PASS");
    else
      $display(
        "PROBE p15 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
