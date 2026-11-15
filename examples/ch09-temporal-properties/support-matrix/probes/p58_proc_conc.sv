// A concurrent assertion in procedural code takes its clock from the
// always_ff and its enable from the if around it: ok is false at t == 2,
// where en is low, and at t == 6 in the BAD instance, where en is high
// (p58)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire en = (t >= 4'd4);
  wire ok = (t != 4'd2) && !(BAD && t == 4'd6);
  always_ff @(posedge clk) begin
    if (en) begin
      a1: assert property (ok) else nf++;
    end
  end
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
      $display("PROBE p58 PASS");
    else
      $display(
        "PROBE p58 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
