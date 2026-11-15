// An immediate cover in SBY's cover mode: c counts 0 to 3, so c == 3 is
// reached; the BAD variant covers c == 15, which is unreachable, and the
// task must FAIL (p69)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] c = 0;                 // counts 0 to 3
  always_ff @(posedge clk) c <= (c == 4'd3) ? 4'd0 : c + 4'd1;
  always @(posedge clk) c1: cover (c == (BAD ? 4'd15 : 4'd3));
endmodule
