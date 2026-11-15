// The property of p67 under abc pdr, which is to find the strengthening (c
// <= 3) itself: expected PASS. The BAD variant asserts c != 3 and must
// FAIL (p68)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] c = 0;                 // counts 0 to 3
  always_ff @(posedge clk) c <= (c == 4'd3) ? 4'd0 : c + 4'd1;
  always @(posedge clk) a1: assert (c != (BAD ? 4'd3 : 4'd15));
endmodule
