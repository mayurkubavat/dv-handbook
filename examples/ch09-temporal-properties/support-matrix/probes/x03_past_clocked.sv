// $past in a clocked immediate assertion: $past(t) is t - 1 from the
// second tick on; the BAD instance expects a wrong value at t == 5 (x03)
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
  always @(posedge clk)
    if (t != 4'd0) a1: assert ($past(t) == prev) `COUNT;
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
      $display("PROBE x03 PASS");
    else
      $display(
        "PROBE x03 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
