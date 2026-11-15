// $onehot, $onehot0 and $countones in clocked immediate assertions, with
// the vector of p36: two bits set at t == 5 in the BAD instance, three
// failures (x06)
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
  wire [3:0] v = (BAD && t == 4'd5) ? 4'b0011 : 4'b0001 << t[1:0];
  always @(posedge clk) begin
    a1: assert ($onehot(v)) `COUNT;
    a2: assert ($onehot0(v)) `COUNT;
    a3: assert ($countones(v) == 1) `COUNT;
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
    if (good.nf == 0 && bad.nf == 3)
      $display("PROBE x06 PASS");
    else
      $display(
        "PROBE x06 FAIL failures good=%0d bad=%0d, want 0 and 3",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
