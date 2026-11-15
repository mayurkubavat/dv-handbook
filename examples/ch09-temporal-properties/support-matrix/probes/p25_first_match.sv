// first_match: a at t == 2, b at t == 3 and t == 5, c at t == 3 only. With
// first_match only the match ending at t == 3 counts, so the good instance
// passes (without it, t == 5 would fail); c is absent in the BAD instance
// (p25)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = (t == 4'd3) || (t == 4'd5);
  wire c = (t == 4'd3) && !BAD;
  a1: assert property (@(posedge clk)
    first_match(a ##[1:3] b) |-> c) else nf++;
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
      $display("PROBE p25 PASS");
    else
      $display(
        "PROBE p25 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
