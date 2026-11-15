// until, s_until and until_with: a holds from t == 2 to 5 and b comes at t
// == 5. In the BAD instance a drops at t == 4, before b, and each of the
// three assertions fails once (p42)
module dut #(parameter bit BAD = 0) (input logic clk);
  int nf = 0;
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  wire go = (t == 4'd2);
  wire a = (t >= 4'd2) && (t <= 4'd5) && !(BAD && t == 4'd4);
  wire b = (t == 4'd5);
  a1: assert property (@(posedge clk) go |-> (a until b))
    else nf++;
  a2: assert property (@(posedge clk) go |-> (a s_until b))
    else nf++;
  a3: assert property (@(posedge clk) go |-> (a until_with b))
    else nf++;
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
    if (good.nf == 0 && bad.nf == 3)
      $display("PROBE p42 PASS");
    else
      $display(
        "PROBE p42 FAIL failures good=%0d bad=%0d, want 0 and 3",
        good.nf, bad.nf);
    $finish;
  end
endmodule
`endif
