// cover sequence counts every match: a at t == 2, b at t == 3 and t == 4,
// so a ##[1:2] b matches twice; b is absent in the BAD instance (p51)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int nc = 0;
  wire a = (t == 4'd2);
  wire b = !BAD && (t == 4'd3 || t == 4'd4);
  c1: cover sequence (@(posedge clk) a ##[1:2] b) nc++;
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
    if (good.nc == 2 && bad.nc == 0)
      $display("PROBE p51 PASS");
    else
      $display(
        "PROBE p51 FAIL hits good=%0d bad=%0d, want 2 and 0",
        good.nc, bad.nc);
    $finish;
  end
endmodule
`endif
