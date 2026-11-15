// Zero-time glitch: b follows a through a second always_comb, so for an
// instant after each clock a != b. An immediate assertion may see that
// instant; the standard leaves the order open, so the probe only requires
// the real mismatch (BAD, t == 5) to be reported and prints how often the
// glitch was (p03)
// The failure is counted through an event, so that the always_comb does
// not read what it writes; the native Yosys front end has no action
// blocks, so the count is compiled only for simulation.
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
  logic a = 0;
  logic b;
  always_ff @(posedge clk) a <= ~a;
  always_comb g1: assert (a == b) `COUNT;
  always_comb b = a ^ (BAD && t == 4'd5);
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
    if (bad.nf >= 1)
      $display(
        "PROBE p03 PASS glitch reported %0d times in 14 ticks",
        good.nf);
    else
      $display(
        "PROBE p03 FAIL real mismatch not reported, bad=%0d",
        bad.nf);
    $finish;
  end
endmodule
`endif
