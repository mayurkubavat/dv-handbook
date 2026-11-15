// assume as a constraint on a free input: with d < 8 assumed, d != 12
// holds; the BAD variant assumes only d < 16 and the assertion fails (p48)
module dut #(parameter bit BAD = 0) (
  input logic clk,
  input logic [3:0] d
);
  always @(posedge clk) begin
    m1: assume ({1'b0, d} < (BAD ? 5'd16 : 5'd8));
    a1: assert (d != 4'd12);
  end
endmodule
