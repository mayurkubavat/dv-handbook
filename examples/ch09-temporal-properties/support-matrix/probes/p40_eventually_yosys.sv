// Liveness for SBY's live mode, in the native front end's spelling (no
// clock): t reaches 5, which the BAD variant denies (p40)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  a1: assert property (s_eventually (t == 4'd5 && !BAD));
endmodule
