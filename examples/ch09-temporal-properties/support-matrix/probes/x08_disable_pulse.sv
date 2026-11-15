// disable iff pulsed between clock edges: a at t == 2 starts an attempt
// that must fail at t == 5. rst pulses for 2 ns after the falling edge in
// t == 4, high at no rising edge; disable iff is not sampled, so the
// attempt is aborted. The BAD instance has no pulse and must report the
// failure (x08)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  logic rst = 0;
  wire a = (t == 4'd2);
  wire b = 1'b0;
  always @(negedge clk) if (!BAD && t == 4'd4) begin
    rst = 1;
    #2 rst = 0;
  end
  a1: assert property (@(posedge clk) disable iff (rst)
    a |-> ##3 b) else nf++;
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
    if (good.nf == 0 && bad.nf == 1)
      $display("PROBE x08 PASS");
    else
      $display(
        "PROBE x08 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
