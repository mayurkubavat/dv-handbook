// $initstate, a Yosys system function, as the first-step guard of $past,
// behind `ifdef FORMAL so that a simulator never sees it. $past(t) is t -
// 1; the BAD instance expects a wrong value at t == 5 (p66)
// The native Yosys front end has no action blocks, so the failure count
// is compiled only for simulation.
`ifdef FORMAL
`define COUNT
`else
`define COUNT else nf++
`endif
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire [3:0] prev = t - 4'd1 - {3'd0, BAD && t == 4'd5};
`ifdef FORMAL
  wire first = $initstate;
`else
  wire first = (t == 4'd0);
`endif
  always @(posedge clk)
    if (!first) a1: assert ($past(t) == prev) `COUNT;
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
      $display("PROBE p66 PASS");
    else
      $display(
        "PROBE p66 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
