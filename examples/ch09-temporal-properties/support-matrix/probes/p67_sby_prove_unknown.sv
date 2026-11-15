// A true property that 5-induction cannot prove: c counts 0 to 3, so c !=
// 15 holds, but the unreachable states 10 to 14 satisfy it for five steps
// and then reach 15. Expected UNKNOWN. The BAD variant asserts c != 3 and
// must FAIL (p67)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] c = 0;                 // counts 0 to 3
  always_ff @(posedge clk) c <= (c == 4'd3) ? 4'd0 : c + 4'd1;
  always @(posedge clk) a1: assert (c != (BAD ? 4'd3 : 4'd15));
endmodule
