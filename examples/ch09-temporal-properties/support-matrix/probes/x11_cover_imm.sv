// Immediate cover in a clocked always block, counted by its statement: hit
// once at t == 5, never in the BAD instance (x11)
module dut #(parameter bit BAD = 0) (input logic clk);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  int nc = 0;
  wire hit = (t == 4'd5) && !BAD;
`ifdef FORMAL
  always @(posedge clk) c1: cover (hit);
`else
  always @(posedge clk) c1: cover (hit) nc++;
`endif
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
    if (good.nc == 1 && bad.nc == 0)
      $display("PROBE x11 PASS");
    else
      $display(
        "PROBE x11 FAIL hits good=%0d bad=%0d, want 1 and 0",
        good.nc, bad.nc);
    $finish;
  end
endmodule
`endif
