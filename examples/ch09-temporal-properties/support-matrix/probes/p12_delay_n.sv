// a ##2 b as a consequent: a at t == 2 and t == 6, b two ticks after each,
// except after the second in the BAD instance (p12)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2) || (t == 4'd6);
  wire b = (t == 4'd4) || (t == 4'd8 && !BAD);
  a1: assert property (@(posedge clk) a |-> a ##2 b) else nf++;
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
      $display("PROBE p12 PASS");
    else
      $display(
        "PROBE p12 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
