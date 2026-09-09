// tb_fourstate.sv -- run the unreset design and report what is visible.
//
// Under a four-state simulator `state` starts unknown, and the report says
// so. Under a two-state simulator it starts at some definite value, and the
// design looks like it works. Neither tool is wrong; they model different
// things, and a reader has to know which question each can answer.
module tb_fourstate;
  logic       clk = 1'b0;
  logic       go = 1'b0;
  logic [7:0] out;

  dut_unreset u (.clk(clk), .go(go), .out(out));
  initial forever #5 clk = ~clk;

  initial begin
    @(negedge clk);
    go = 1'b1;
    repeat (3) @(posedge clk);
    #1;
    // One run cannot tell whether a definite value is meaningful, so the
    // testbench reports what it saw and leaves the conclusion to whoever
    // compares the runs.
    if (out === 8'hxx) $display("out is unknown");
    else               $display("out = %0d", out);
    $finish;
  end
endmodule
