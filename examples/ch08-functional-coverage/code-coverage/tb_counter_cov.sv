// tb_counter_cov.sv -- the Appendix F counter driven for +n=<cycles>
// enabled cycles, with two cover properties. Built with --coverage, the
// run writes coverage.dat with line, toggle, branch, expression and
// cover-property records; the runner script reads that file back.
// No class is used, so no standard-library records land in the file.
`timescale 1ns/1ps
module tb_counter_cov;
  logic       clk = 0;
  logic       rst_n;
  logic       en;
  logic [7:0] count;
  int         n;

  counter dut (.clk, .rst_n, .en, .count);

  always #5 clk <= ~clk;

  // Counts clock edges at which the property held, not a 0/1 "hit".
  // Neither property reads rst_n: a property that samples an
  // asynchronous reset at a clock is a SYNCASYNCNET error under -Wall.
  cov_counting: cover property (@(posedge clk) en);
  cov_wrap:     cover property (@(posedge clk) count == 8'hff);

  initial begin
    if (!$value$plusargs("n=%d", n)) n = 10;
    rst_n = 0; en = 0;
    repeat (2) @(posedge clk);
    rst_n <= 1;
    en    <= 1;
    repeat (n) @(posedge clk);
    en <= 0;
    @(posedge clk); #1;
    if (count == 8'(n))
      $display("count=%0d after %0d enabled cycles", count, n);
    else
      $display("FAIL: count=%0d after %0d enabled cycles", count, n);
    $finish;
  end
endmodule
