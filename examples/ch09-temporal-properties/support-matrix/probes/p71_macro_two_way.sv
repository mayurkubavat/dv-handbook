// One macro, two expansions: a concurrent assertion with a failure count
// for simulation, a clocked immediate assertion under FORMAL. ok is false
// at t == 5 in the BAD instance only (p71)
`ifdef FORMAL
`define ASSERT(name, expr) \
  always @(posedge clk) name: assert (expr);
`else
`define ASSERT(name, expr) \
  name: assert property (@(posedge clk) expr) else nf++;
`endif
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = !(BAD && t == 4'd5);
  `ASSERT(a1, ok)
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
      $display("PROBE p71 PASS");
    else
      $display(
        "PROBE p71 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
