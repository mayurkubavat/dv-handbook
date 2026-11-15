// $past(t) equals t - 1 from the second tick on; the BAD instance expects
// a wrong value at t == 5. The first tick is excluded from the assertion,
// and what $past returns there is printed instead, for a net, for a
// variable set in an initial block and for one with a declaration
// initializer (p30)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire [3:0] prev = t - 4'd1 - {3'd0, BAD && t == 4'd5};
  wire [3:0] tn = ~t;                // a net: 15 on the first tick
  logic [3:0] q;                     // set in an initial block: 6
  initial q = 4'd6;
  logic [3:0] r = 4'd5;              // a declaration initializer: 5
  logic [3:0] f_tn, f_q, f_r;
  always_ff @(posedge clk)
    if (t == 4'd0) begin
      f_tn <= $past(tn);
      f_q <= $past(q);
      f_r <= $past(r);
    end
  a1: assert property (@(posedge clk)
    (t == 4'd0) || ($past(t) == prev)) else nf++;
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
    if (good.nf == 0 && bad.nf == 1) begin
      $write("PROBE p30 PASS first-tick $past: net %0d, ", good.f_tn);
      $display("initial-block %0d, initializer %0d", good.f_q, good.f_r);
    end else
      $display(
        "PROBE p30 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
