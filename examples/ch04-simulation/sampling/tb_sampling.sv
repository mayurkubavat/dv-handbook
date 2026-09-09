// tb_sampling.sv -- why a monitor reports a value that is correct and old.
//
// The design is a register: q takes d on every rising edge. Three watchers
// look at the same edge and report three different things, and all three
// are behaving exactly as the language says they should.
//
//   at the edge   reads q in the same region the design's update is
//                 scheduled from, so it sees the value from *before* this
//                 edge. This is the stale monitor, and it is the most
//                 common first bug in a new testbench.
//   after it      waits for the non-blocking updates to be applied, so it
//                 sees the value this edge produced.
//   $strobe       does the same thing without a delay, by observing after
//                 the updates rather than by waiting a nanosecond.
//
// Nothing here is broken. What is broken is a scoreboard that pairs the
// stale read with a stimulus value that has already moved on.
module dut (input logic clk, input logic [7:0] d, output logic [7:0] q);
  always_ff @(posedge clk) q <= d;
endmodule

module tb_sampling;
  logic       clk = 1'b0;
  logic [7:0] d = 8'd10, q;

  dut u (.clk(clk), .d(d), .q(q));
  initial forever #5 clk = ~clk;

  always @(posedge clk) d <= d + 8'd1;

  always @(posedge clk)
    $display("t=%0t  at the edge : q=%0d", $time, q);

  always @(posedge clk)
    $strobe("t=%0t  $strobe     : q=%0d", $time, q);

  initial begin
    $display("three watchers, one edge, and d rising 10, 11, 12 ...");
    repeat (3) begin
      @(posedge clk);
      #1 $display("t=%0t  after it    : q=%0d", $time, q);
    end
    $finish;
  end
endmodule
