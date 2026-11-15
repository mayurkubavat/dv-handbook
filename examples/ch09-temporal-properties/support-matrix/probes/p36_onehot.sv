// $onehot, $onehot0, $countones and $isunknown on a one-hot vector that
// has two bits set at t == 5 in the BAD instance, where the first three
// assertions fail (p36)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire [3:0] v = (BAD && t == 4'd5) ? 4'b0011 : 4'b0001 << t[1:0];
  a1: assert property (@(posedge clk) $onehot(v)) else nf++;
  a2: assert property (@(posedge clk) $onehot0(v)) else nf++;
  a3: assert property (@(posedge clk) $countones(v) == 1) else nf++;
  a4: assert property (@(posedge clk) !$isunknown(v)) else nf++;
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
    if (good.nf == 0 && bad.nf == 3)
      $display("PROBE p36 PASS");
    else
      $display(
        "PROBE p36 FAIL failures good=%0d bad=%0d, want 0 and 3",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
