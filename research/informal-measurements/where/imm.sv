// Immediate assertions only: one false (q reaches 9), one true.
module imm(input logic clk, input logic rst, input logic en, output logic [3:0] q);
  initial q = 4'd0;
  always_ff @(posedge clk)
    if (rst) q <= '0;
    else if (en && q != 4'd9) q <= q + 4'd1;
  always_ff @(posedge clk) if (!rst) a_false: assert (q != 4'd9);
  always_comb a_true: assert (q != 4'd12 || rst);
endmodule
