// tb_vacuity.sv -- drives requests only when +traffic is given, which
// stands for any testbench whose stimulus never reached the scenario.
`timescale 1ns/1ps
module tb_vacuity;
  logic clk = 0, req = 0, ack;
  always #5 clk <= ~clk;
  responder dut (.*);

  initial begin
    for (int i = 0; i < 20; i++) begin
      @(negedge clk);
      req = $test$plusargs("traffic") && (i % 4 == 1);
    end
    @(negedge clk);
    $display("test finished: 21 ticks");
    $finish;
  end
endmodule
