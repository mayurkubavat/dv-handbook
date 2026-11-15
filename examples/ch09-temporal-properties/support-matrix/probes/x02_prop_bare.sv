// assert property with a bare expression and no clock, at module level,
// which the standard does not accept without a default clocking: ok is false at t == 5 in the BAD instance
// only (x02)
// The failure count is simulation code: a formal run defines FORMAL,
// which compiles it out.
`ifdef FORMAL
`define COUNT
`else
`define COUNT else nf++
`endif
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = !(BAD && t == 4'd5);
  a1: assert property (ok) `COUNT;
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
      $display("PROBE x02 PASS");
    else
      $display(
        "PROBE x02 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
