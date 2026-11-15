// A concurrent assertion written inside an interface, which the design
// instantiates: a at t == 3; b with it, except in the BAD instance (x17)
`ifdef FORMAL
`define COUNT
`else
`define COUNT else nf++
`endif
interface hs_if (input logic clk, input logic a, input logic b);
  int nf = 0;
  a1: assert property (@(posedge clk) !a || b) `COUNT;
endinterface
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd3);
  wire b = (t == 4'd3) && !BAD;
  hs_if u_if (.clk, .a, .b);
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
    if (good.u_if.nf == 0 && bad.u_if.nf == 1)
      $display("PROBE x17 PASS");
    else
      $display(
        "PROBE x17 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.u_if.nf, bad.u_if.nf);
    $finish;
  end
endmodule
`endif
