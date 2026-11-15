// Sequence or in a consequent when neither operand matches: a at t == 2,
// then b one tick later or d two ticks later; both come in the good
// instance and neither in the BAD one, which must fail (x15)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = (t == 4'd3) && !BAD;
  wire d = (t == 4'd4) && !BAD;
  a1: assert property (@(posedge clk)
    a |-> (a ##1 b) or (a ##2 d)) else nf++;
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
      $display("PROBE x15 PASS");
    else
      $display(
        "PROBE x15 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
