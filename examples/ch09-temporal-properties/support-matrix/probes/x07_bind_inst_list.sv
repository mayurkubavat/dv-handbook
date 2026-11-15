// bind with a target scope and an instance list (bind leaf: u1 ...): as
// p56, only u1 of each dut is to get a checker (x07)
`ifndef FORMAL
package pk;
  int nbound = 0;             // how many checkers exist
endpackage
`endif
module leaf #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = !(BAD && t == 4'd5);
endmodule
module leaf_sva (input logic clk, input logic ok);
  int nf = 0;
`ifndef FORMAL
  initial pk::nbound++;
`endif
  a1: assert property (@(posedge clk) ok) else nf++;
endmodule
module dut #(parameter bit BAD = 0) (input logic clk);
  leaf #(.BAD(1)) u0 (.clk);       // always wrong, not bound
  leaf #(.BAD(BAD)) u1 (.clk);
  bind leaf: u1 leaf_sva chk (.*);
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
    if (good.u1.chk.nf == 0 && bad.u1.chk.nf == 1
        && pk::nbound == 2)
      $display("PROBE x07 PASS");
    else
      $display(
        "PROBE x07 FAIL failures good=%0d bad=%0d, checkers=%0d",
        good.u1.chk.nf, bad.u1.chk.nf, pk::nbound);
    $finish;
  end
endmodule
`endif
