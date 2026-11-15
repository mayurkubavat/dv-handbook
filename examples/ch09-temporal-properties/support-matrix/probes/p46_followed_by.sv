// Followed-by: a at t == 2, then b one tick later (#=#) and c on the same
// tick (#-#); both are absent in the BAD instance, one failure each (p46)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire a = (t == 4'd2);
  wire b = (t == 4'd3) && !BAD;
  wire c = (t == 4'd2) && !BAD;
  a1: assert property (@(posedge clk) a |-> (a #=# b)) else nf++;
  a2: assert property (@(posedge clk) a |-> (a #-# c)) else nf++;
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
    if (good.nf == 0 && bad.nf == 2)
      $display("PROBE p46 PASS");
    else
      $display(
        "PROBE p46 FAIL failures good=%0d bad=%0d, want 0 and 2",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
