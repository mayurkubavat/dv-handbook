// $rose and $fell: s is high from t == 3 to 5; v goes 2, 3, 2 so its bit 0
// rises at t == 4; w goes 0 to 2, which is not a rise because only bit 0
// counts. In the BAD instance s rises one tick late, so the first
// assertion fails at t == 3 and at t == 4 (p33)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire s = (t >= (BAD ? 4'd4 : 4'd3)) && (t <= 4'd5);
  wire [1:0] v = (t >= 4'd4 && t <= 4'd6) ? 2'd3 : 2'd2;
  wire [1:0] w = (t >= 4'd4) ? 2'd2 : 2'd0;
  wire g = (t == 4'd0);          // the first tick is p30's
  a1: assert property (@(posedge clk) g || ($rose(s) == (t == 4'd3)))
    else nf++;
  a2: assert property (@(posedge clk) g || ($fell(s) == (t == 4'd6)))
    else nf++;
  a3: assert property (@(posedge clk) g || ($rose(v) == (t == 4'd4)))
    else nf++;
  a4: assert property (@(posedge clk) g || !$rose(w)) else nf++;
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
      $display("PROBE p33 PASS");
    else
      $display(
        "PROBE p33 FAIL failures good=%0d bad=%0d, want 0 and 2",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
