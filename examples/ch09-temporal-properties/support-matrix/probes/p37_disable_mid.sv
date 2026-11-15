// disable iff in mid-attempt: a at t == 2 starts an attempt that must fail
// at t == 5, since b never comes. rst is high at t == 3 and 4, which
// aborts it; the BAD instance has no reset and must report the failure
// (p37)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = 1'b0;
  wire rst = !BAD && (t == 4'd3 || t == 4'd4);
  a1: assert property (@(posedge clk) disable iff (rst)
    a |-> ##3 b) else nf++;
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
      $display("PROBE p37 PASS");
    else
      $display(
        "PROBE p37 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
