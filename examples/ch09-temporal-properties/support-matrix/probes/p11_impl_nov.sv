// a |=> b beside a |-> ##1 b, which the standard defines as the same
// property: a at t == 3 and t == 6, b one tick after each, except after
// the second in the BAD instance. Both must fail once there and never in
// the good instance; their pass counts, which should agree, are printed
// (p11)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int np1 = 0, nf1 = 0, np2 = 0, nf2 = 0;
  wire a = (t == 4'd3) || (t == 4'd6);
  wire b = (t == 4'd4) || (t == 4'd7 && !BAD);
  a1: assert property (@(posedge clk) a |=> b) np1++;
    else nf1++;
  a2: assert property (@(posedge clk) a |-> ##1 b) np2++;
    else nf2++;
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
    if (good.nf1 == 0 && good.nf2 == 0 && bad.nf1 == 1
        && bad.nf2 == 1)
      $display(
        "PROBE p11 PASS passes |=> %0d, %0d; ##1 %0d, %0d",
        good.np1, bad.np1, good.np2, bad.np2);
    else
      $display(
        "PROBE p11 FAIL failures |=> %0d, %0d; ##1 %0d, %0d; want 0, 1",
        good.nf1, bad.nf1, good.nf2, bad.nf2);
    $finish;
  end
endmodule
`endif
