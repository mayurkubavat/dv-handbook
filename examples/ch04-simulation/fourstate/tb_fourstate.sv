// tb_fourstate.sv -- run the unreset design and report what is visible.
//
// Under a four-state simulator `state` starts unknown, and the report says
// so. Under a two-state simulator it starts at some definite value, and the
// design looks like it works. Neither tool is wrong; they model different
// things, and a reader has to know which question each can answer.
module tb_fourstate;
  logic       clk = 1'b0;
  logic       go = 1'b0;
  logic [7:0] out_bare, out_else;

  dut_unreset u (.clk(clk), .go(go),
                 .out_bare(out_bare), .out_else(out_else));
  initial forever #5 clk = ~clk;

  initial begin
    @(negedge clk);
    go = 1'b1;
    repeat (3) @(posedge clk);
    #1;
    // One run cannot tell whether a definite value is meaningful, so the
    // testbench reports what it saw and leaves the conclusion to whoever
    // compares the runs.
    if (out_bare === 8'hxx) $display("bare if: out is unknown");
    else                    $display("bare if: out = %0d", out_bare);
    if (out_else === 8'hxx) $display("if/else: out is unknown");
    else                    $display("if/else: out = %0d", out_else);
    $finish;
  end
endmodule
