// Deferred immediate assertion #0 over the same zero-time glitch as p03:
// the glitch must not be reported, the real mismatch (BAD, t == 5) must
// be, once (p04)
// A deferred action block may only be a subroutine call; the call
// triggers an event, so that the always_comb does not read what it
// writes. Compiled only for simulation.
`ifdef FORMAL
`define COUNT
`else
`define COUNT else bump()
`endif
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
`ifndef FORMAL
  event failed;
  always @(failed) nf++;
  function void bump(); -> failed; endfunction
`endif
  logic a = 0;
  logic b;
  always_ff @(posedge clk) a <= ~a;
  always_comb g1: assert #0 (a == b) `COUNT;
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
    if (good.nf == 0 && bad.nf == 1)
      $display("PROBE p04 PASS");
    else
      $display(
        "PROBE p04 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
