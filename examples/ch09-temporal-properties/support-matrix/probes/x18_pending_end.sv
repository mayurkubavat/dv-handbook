// An obligation still pending when the run ends. a at t == 12 of 14
// ticks; b at t == 13 when GOOD is defined, never otherwise. One build
// for each operator, chosen by a define: OP_SEV s_eventually, OP_UNB
// ##[1:$], OP_RNG ##[1:3], OP_UNTIL until, OP_SUNTIL s_until. The
// runner reads the failures counted by the action block before $finish
// and in a final block, any report printed after $finish, and the exit
// status (x18)
module top;
  bit clk;
  always #5 clk = ~clk;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd12);
`ifdef GOOD
  wire b = (t == 4'd13);
`else
  wire b = 1'b0;
`endif
  int nf = 0;
`ifdef OP_SEV
  a1: assert property (@(posedge clk) a |-> s_eventually b) else nf++;
`elsif OP_UNB
  a1: assert property (@(posedge clk) a |-> ##[1:$] b) else nf++;
`elsif OP_RNG
  a1: assert property (@(posedge clk) a |-> ##[1:3] b) else nf++;
`elsif OP_UNTIL
  a1: assert property (@(posedge clk) a |-> (1'b1 until b)) else nf++;
`else
  a1: assert property (@(posedge clk) a |-> (1'b1 s_until b)) else nf++;
`endif
  initial begin
    repeat (14) @(posedge clk);
    #1;
    $display("PROBE x18 PASS %0d failures before $finish", nf);
    $finish;
  end
  final $display("FINAL x18 %0d failures", nf);
endmodule
