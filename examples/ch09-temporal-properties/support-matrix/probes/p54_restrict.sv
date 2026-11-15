// restrict property: in simulation it is not checked, so d == 9, which
// violates it, must not be reported. In formal it constrains the free
// input d as an assumption does: d != 12 holds under d < 8 and fails in
// the BAD variant's d < 16 (p54)
module dut #(parameter bit BAD = 0) (
  input logic clk,
  input logic [3:0] d
);
  int nf = 0;
  r1: restrict property (@(posedge clk)
    {1'b0, d} < (BAD ? 5'd16 : 5'd8));
  a1: assert property (@(posedge clk) d != 4'd12) else nf++;
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut u (.clk, .d(4'd9));
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (u.nf == 0)
      $display("PROBE p54 PASS");
    else
      $display(
        "PROBE p54 FAIL failures=%0d, want 0",
        u.nf);
    $finish;
  end
endmodule
`endif
