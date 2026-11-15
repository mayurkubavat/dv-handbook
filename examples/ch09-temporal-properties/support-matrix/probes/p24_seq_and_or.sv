// Sequence and / or over (a ##1 b) and (a ##2 d), started at t == 2 and t
// == 7. In the BAD instance b never comes and d comes only after the first
// start: `and` fails twice, `or` once (p24)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int nfa = 0, nfo = 0;
  wire a = (t == 4'd2) || (t == 4'd7);
  wire b = !BAD && (t == 4'd3 || t == 4'd8);
  wire d = (t == 4'd4) || (t == 4'd9 && !BAD);
  a1: assert property (@(posedge clk)
    a |-> (a ##1 b) and (a ##2 d)) else nfa++;
  a2: assert property (@(posedge clk)
    a |-> (a ##1 b) or (a ##2 d)) else nfo++;
endmodule
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut #(.BAD(0)) good (.clk);
  dut #(.BAD(1)) bad (.clk);
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (good.nfa == 0 && good.nfo == 0 && bad.nfa == 2
        && bad.nfo == 1)
      $display("PROBE p24 PASS");
    else
      $display(
        "PROBE p24 FAIL and/or good=%0d/%0d bad=%0d/%0d, want 0/0 and 2/1",
        good.nfa, good.nfo, bad.nfa, bad.nfo);
    $finish;
  end
endmodule
`endif
