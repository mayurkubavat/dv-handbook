// tb_race.sv -- run one design for a few cycles and print what it saw.
//
// The testbench is deliberately dull: it makes a clock, releases reset, and
// prints. All the interesting behaviour is in the design under test, so any
// difference between two simulators is the design's ordering and not the
// testbench's.
//
// DUT is chosen at compile time with -DDUT_RACY or -DDUT_SAFE so that both
// designs go through an identical harness.
module tb_race;
  logic       clk = 1'b0;
  logic       rst_n = 1'b0;
  logic [7:0] count, observed;

`ifdef DUT_RACY
  racy dut (.clk(clk), .rst_n(rst_n), .count(count), .observed(observed));
  localparam string WHICH = "racy";
`else
  safe dut (.clk(clk), .rst_n(rst_n), .count(count), .observed(observed));
  localparam string WHICH = "safe";
`endif

  // In an initial block rather than an always block, so that a lint of
  // this file has no reason to waive the warning about blocking
  // assignments in sequential logic -- which the racing design earns.
  initial forever #5 clk = ~clk;

  initial begin
    $display("design=%0s", WHICH);
    repeat (2) @(negedge clk);
    rst_n = 1'b1;
    repeat (4) begin
      @(posedge clk);
      // Wait for the non-blocking updates of this timestep to settle before
      // printing, so the report is of the values the cycle ended with.
      #1;
      $display("count=%0d observed=%0d", count, observed);
    end
    $finish;
  end
endmodule
