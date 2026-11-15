// A clocked immediate assertion with no action block fails once, at
// t == 5. The runner reports whether the failure was printed, whether
// the run reached its end, and the simulator's exit status (x16)
module dut (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  always @(posedge clk) a1: assert (t != 4'd5);
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut u (.clk);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    $display("PROBE x16 PASS");
    $finish;
  end
endmodule
`endif
