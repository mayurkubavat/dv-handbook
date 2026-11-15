// a |=> b beside a |-> ##1 b with attempts on consecutive ticks: a at t ==
// 2, 3 and 4, b at t == 3, 4 and 5, except t == 5 in the BAD instance.
// Both must fail once there; their pass counts, which should agree, are
// printed (x09)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int np1 = 0, nf1 = 0, np2 = 0, nf2 = 0;
  wire a = (t >= 4'd2) && (t <= 4'd4);
  wire b = (t >= 4'd3) && (t <= (BAD ? 4'd4 : 4'd5));
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
        "PROBE x09 PASS passes |=> %0d, %0d; ##1 %0d, %0d",
        good.np1, bad.np1, good.np2, bad.np2);
    else
      $display(
        "PROBE x09 FAIL failures |=> %0d, %0d; ##1 %0d, %0d; want 0, 1",
        good.nf1, bad.nf1, good.nf2, bad.nf2);
    $finish;
  end
endmodule
`endif
