// program block as the testbench container
module dut(input logic clk, input logic [7:0] d, output logic [7:0] q);
  always_ff @(posedge clk) q <= d;
endmodule

program tb(input logic clk, output logic [7:0] d, input logic [7:0] q);
  initial begin
    d = 8'h00;
    @(posedge clk); d = 8'h3C;    // program blocks run in the Reactive region
    @(posedge clk); @(posedge clk);
    $display("q=%h", q);
    if (q == 8'h3C) $display("PROBE p17 PASS");
    else $display("PROBE p17 FAIL");
    $finish;
  end
endprogram

module top;
  logic clk = 0; logic [7:0] d, q;
  always #5 clk <= ~clk;
  dut u(.clk(clk), .d(d), .q(q));
  tb  t(.clk(clk), .d(d), .q(q));
endmodule
