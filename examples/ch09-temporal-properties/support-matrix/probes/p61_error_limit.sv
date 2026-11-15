// Two assertions with no action block, failing at t == 3 and at t == 6.
// The runner runs the binary twice and counts reported failures: by
// default the first one ends the run; with +verilator+error+limit+10 both
// are reported and the run reaches its end (p61)
module dut (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  a1: assert property (@(posedge clk) t != 4'd3);
  a2: assert property (@(posedge clk) t != 4'd6);
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut u (.clk);
  initial begin
    repeat (14) @(posedge clk);
    $display("PROBE p61 PASS");
    $finish;
  end
endmodule
`endif
