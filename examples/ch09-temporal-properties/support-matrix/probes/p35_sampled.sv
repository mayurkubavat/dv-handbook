// $sampled in an action block: the assertion fails on the tick that
// samples t == 3. The action block runs after the clock edge has moved t
// on, so t reads 4 there and $sampled(t) must read 3 (p35)
module dut (input logic clk);
  int nf = 0;
  logic [3:0] now, smp;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  a1: assert property (@(posedge clk) t != 4'd3)
    else begin nf++; now = t; smp = $sampled(t); end
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut u (.clk);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (u.nf == 1 && u.smp == 4'd3)
      $display(
        "PROBE p35 PASS t reads %0d, $sampled(t) reads %0d",
        u.now, u.smp);
    else
      $display(
        "PROBE p35 FAIL failures=%0d, $sampled(t)=%0d, want 1 and 3",
        u.nf, u.smp);
    $finish;
  end
endmodule
`endif
