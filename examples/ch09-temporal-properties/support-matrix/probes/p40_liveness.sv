// Liveness as a proof obligation: t reaches 5, which the BAD variant
// denies. No finite run decides the property, so there is no
// simulation half; the tick counter wraps, and the formal tool has to
// show that every loop of the design passes through t == 5 (p40)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  a1: assert property (@(posedge clk) s_eventually (t == 4'd5 && !BAD));
endmodule
