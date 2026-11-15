// $stable and $changed in clocked immediate assertions, with the signals
// of p34: the BAD instance expects the change one tick late, so each
// assertion fails twice (x05)
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
  wire x = (t >= 4'd4);
  wire e = (t == (BAD ? 4'd5 : 4'd4));
  wire g = (t == 4'd0);          // the first tick is p30's
  always @(posedge clk) if (!g) begin
    a1: assert ($changed(x) == e) `COUNT;
    a2: assert ($stable(x) == !e) `COUNT;
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
    if (good.nf == 0 && bad.nf == 4)
      $display("PROBE x05 PASS");
    else
      $display(
        "PROBE x05 FAIL failures good=%0d bad=%0d, want 0 and 4",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
