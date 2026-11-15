// SBY's expect option: the runner adds `expect fail` and reads the exit
// status. The BAD variant fails at step 5, as expected, so sby must exit
// 0; the good variant passes, unexpectedly, so sby must exit non-zero
// (p70)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = !(BAD && t == 4'd5);
  always @(posedge clk) a1: assert (ok);
endmodule
