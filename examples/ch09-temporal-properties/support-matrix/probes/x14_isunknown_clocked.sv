// $isunknown in clocked immediate assertions: v is always known, so
// !$isunknown(v) holds, and the BAD instance's claim at t == 5 that v is
// unknown must fail (x14)
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
  wire [3:0] v = 4'b0001 << t[1:0];
  always @(posedge clk) begin
    a1: assert (!$isunknown(v)) `COUNT;
    if (BAD && t == 4'd5) a2: assert ($isunknown(v)) `COUNT;
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
      $display("PROBE x14 PASS");
    else
      $display(
        "PROBE x14 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
