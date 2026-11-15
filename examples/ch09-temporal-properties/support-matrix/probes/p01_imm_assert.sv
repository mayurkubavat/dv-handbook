// Immediate assertion in always_comb: ok is false at t == 5 in the BAD
// instance only, so one failure there and none in the good one (p01)
// The failure is counted through an event, so that the always_comb does
// not read what it writes. The count is simulation code: a formal run
// defines FORMAL, which compiles it out.
`ifdef FORMAL
`define COUNT
`else
`define COUNT else -> failed
`endif
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
`ifndef FORMAL
  event failed;
  always @(failed) nf++;
`endif
  wire ok = !(BAD && t == 4'd5);
  always_comb a1: assert (ok) `COUNT;
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
      $display("PROBE p01 PASS");
    else
      $display(
        "PROBE p01 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
