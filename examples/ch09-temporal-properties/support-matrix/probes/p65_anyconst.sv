// (* anyconst *): a Yosys attribute. In formal k is an arbitrary constant,
// so it never changes (a1) but it can be 5 (a2, BAD variant only, must
// fail). A simulator is to ignore the attribute and leave k undriven, at
// x, which the case equalities accept: no failure in either instance (p65)
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
  (* anyconst *) logic [3:0] k;
  logic [3:0] k_q;
  always @(posedge clk) begin
    k_q <= k;
    if (t != 4'd0) a1: assert (k === k_q) `COUNT;
    if (BAD) a2: assert (k !== 4'd5) `COUNT;
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
    if (good.nf == 0 && bad.nf == 0)
      $display(
        "PROBE p65 PASS k reads %b",
        good.k);
    else
      $display(
        "PROBE p65 FAIL failures good=%0d bad=%0d, want 0 and 0",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
