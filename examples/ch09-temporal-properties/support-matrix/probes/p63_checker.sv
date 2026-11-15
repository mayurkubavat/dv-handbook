// checker: a checker instantiated in dut; its failures are counted per
// instance in a package. a at t == 3; b with it, except in the BAD
// instance (p63)
package pk;
  int nf [2];
endpackage
checker chk (logic a, logic b, bit id, logic ck);
  a1: assert property (@(posedge ck) a |-> b) else pk::nf[id]++;
endchecker
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd3);
  wire b = (t == 4'd3) && !BAD;
  chk c1 (a, b, BAD, clk);
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
    if (pk::nf[0] == 0 && pk::nf[1] == 1)
      $display("PROBE p63 PASS");
    else
      $display(
        "PROBE p63 FAIL failures good=%0d bad=%0d, want 0 and 1",
        pk::nf[0], pk::nf[1]);
    $finish;
  end
endmodule
`endif
