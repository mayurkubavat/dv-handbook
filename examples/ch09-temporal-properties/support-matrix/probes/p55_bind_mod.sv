// bind to a module: the checker dut_sva is bound into every dut and
// connected by name to its ports a and b. a at t == 3; b with it, except
// in the BAD instance (p55)
module dut #(parameter bit BAD = 0) (
  input  logic clk,
  output logic a,
  output logic b
);
  logic [3:0] t = 0;                 // step counter: the stimulus
  always_ff @(posedge clk) t <= t + 4'd1;
  assign a = (t == 4'd3);
  assign b = (t == 4'd3) && !BAD;
endmodule
module dut_sva (input logic clk, input logic a, input logic b);
  int nf = 0;
  a1: assert property (@(posedge clk) !a || b) else nf++;
endmodule
bind dut dut_sva chk (.clk(clk), .a(a), .b(b));
`ifndef FORMAL
module top;
  bit clk;
  always #5 clk = ~clk;
  dut #(.BAD(0)) good (.clk, .a(), .b());
  dut #(.BAD(1)) bad (.clk, .a(), .b());
  initial begin
    repeat (14) @(posedge clk);
    #1;
    if (good.chk.nf == 0 && bad.chk.nf == 1)
      $display("PROBE p55 PASS");
    else
      $display(
        "PROBE p55 FAIL failures good=%0d bad=%0d, want 0 and 1",
        good.chk.nf, bad.chk.nf);
    $finish;
  end
endmodule
`endif
