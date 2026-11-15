// cover property of an implication: a and b at t == 2 give one hit. In the
// BAD instance a never comes; the 14 vacuous successes are not to be
// counted, so no hit (p50)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int nc = 0;
  wire a = (t == 4'd2) && !BAD;
  wire b = (t == 4'd2);
  c1: cover property (@(posedge clk) a |-> b) nc++;
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
    if (good.nc == 1 && bad.nc == 0)
      $display("PROBE p50 PASS");
    else
      $display(
        "PROBE p50 FAIL hits good=%0d bad=%0d, want 1 and 0",
        good.nc, bad.nc);
    $finish;
  end
endmodule
`endif
