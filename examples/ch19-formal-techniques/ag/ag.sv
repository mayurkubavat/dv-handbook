// ag.sv -- two blocks that each pass the other's output on, one cycle
// later. blk is proved alone with its input free; ag_top is the two
// of them in a ring, for comparing the composed result. RST1 = 1
// gives a block (or both) a reset value of 1, breaking its guarantee.
module blk #(parameter bit RST1 = 0) (
  input  logic clk, rst_n, in,
  output logic out
);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) out <= RST1;
    else        out <= in;
endmodule

module ag_top #(parameter bit RST1 = 0) (
  input  logic clk, rst_n,
  output logic x, y
);
  blk #(RST1) ua (.clk, .rst_n, .in(y), .out(x));
  blk #(RST1) ub (.clk, .rst_n, .in(x), .out(y));
endmodule
