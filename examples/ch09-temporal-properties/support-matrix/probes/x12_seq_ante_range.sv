// A sequence with a ranged delay as antecedent, matched once at each of
// its three lengths: a at t == 1, 5 and 9, b at t == 2, 7 and 12, one, two
// and three ticks later. c is due with each b and is absent in the BAD
// instance: three failures (x12)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd1) || (t == 4'd5) || (t == 4'd9);
  wire b = (t == 4'd2) || (t == 4'd7) || (t == 4'd12);
  wire c = b && !BAD;
  a1: assert property (@(posedge clk) (a ##[1:3] b) |-> c)
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
    if (good.nf == 0 && bad.nf == 3)
      $display("PROBE x12 PASS");
    else
      $display(
        "PROBE x12 FAIL failures good=%0d bad=%0d, want 0 and 3",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
