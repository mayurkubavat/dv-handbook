// $rose and $fell in clocked immediate assertions, with the signals of
// p33: in the BAD instance s rises one tick late, so the first assertion
// fails at t == 3 and at t == 4 (x04)
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
  wire s = (t >= (BAD ? 4'd4 : 4'd3)) && (t <= 4'd5);
  wire [1:0] v = (t >= 4'd4 && t <= 4'd6) ? 2'd3 : 2'd2;
  wire [1:0] w = (t >= 4'd4) ? 2'd2 : 2'd0;
  wire g = (t == 4'd0);          // the first tick is p30's
  always @(posedge clk) if (!g) begin
    a1: assert ($rose(s) == (t == 4'd3)) `COUNT;
    a2: assert ($fell(s) == (t == 4'd6)) `COUNT;
    a3: assert ($rose(v) == (t == 4'd4)) `COUNT;
    a4: assert (!$rose(w)) `COUNT;
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
    if (good.nf == 0 && bad.nf == 2)
      $display("PROBE x04 PASS");
    else
      $display(
        "PROBE x04 FAIL failures good=%0d bad=%0d, want 0 and 2",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
