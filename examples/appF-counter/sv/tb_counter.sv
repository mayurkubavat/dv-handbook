// tb_counter.sv -- a self-checking testbench with no methodology library.
// It drives reset and enable, counts clock edges itself, and compares.
`timescale 1ns/1ps
module tb_counter;
  logic       clk = 0;
  logic       rst_n;
  logic       en;
  logic [7:0] count;

  counter dut (.clk, .rst_n, .en, .count);

  always #5 clk <= ~clk;                // 100 MHz clock

  int expected = 0;
  int errors   = 0;

  initial begin
    rst_n = 0; en = 0;
    repeat (2) @(posedge clk);
    rst_n = 1;

    // Count for 10 cycles, then pause for 3, then count again.
    drive_enable(10);
    drive_enable(0);
    repeat (3) @(posedge clk);
    drive_enable(5);

    if (errors == 0) $display("PASS: counter reached %0d as expected", count);
    else             $display("FAIL: %0d mismatches", errors);
    $finish;
  end

  // Enable for n cycles and check the count after every edge.
  task automatic drive_enable(int n);
    en = (n > 0);
    repeat (n) begin
      @(posedge clk); #1;               // sample after the flop has updated
      expected++;
      if (count !== expected[7:0]) begin
        errors++;
        $display("MISMATCH at %0t: count=%0d expected=%0d",
                 $time, count, expected);
      end
    end
    en = 0;
  endtask
endmodule
