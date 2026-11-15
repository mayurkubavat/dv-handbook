// Toolchain probe: a clocked immediate assertion that holds (or, with BAD,
// fails at step 5), run through sby from a file with no [engines] section,
// to record what sby does without one (p00)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire ok = !(BAD && t == 4'd5);
  always @(posedge clk) a1: assert (ok);
endmodule
