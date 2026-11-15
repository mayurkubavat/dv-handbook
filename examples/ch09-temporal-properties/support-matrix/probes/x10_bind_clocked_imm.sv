// bind of a checker whose assertion is a clocked immediate one, so that
// the native Yosys front end can show whether it binds: ok is false at t
// == 5 in the BAD instance (x10)
// The native Yosys front end has no action blocks, so the failure count
// is compiled only for simulation.
`ifdef FORMAL
`define COUNT
`else
`define COUNT else nf++
`endif
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = !(BAD && t == 4'd5);
endmodule
module dut_sva (input logic clk, input logic ok);
  int nf = 0;
  always @(posedge clk) a1: assert (ok) `COUNT;
endmodule
bind dut dut_sva chk (.*);
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut #(.BAD(0)) good (.clk);
  dut #(.BAD(1)) bad (.clk);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (good.chk.nf == 0 && bad.chk.nf == 1)
      $display("PROBE x10 PASS");
    else
      $display(
        "PROBE x10 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.chk.nf, bad.chk.nf);
    $finish;
  end
endmodule
`endif
