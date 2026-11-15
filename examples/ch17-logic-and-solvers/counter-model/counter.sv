// counter.sv -- a 3-bit counter that is meant to stop at 5.
module counter (
  input  logic       clk,
  input  logic       en,
  output logic [2:0] q
);
  logic [2:0] count = 3'd0;         // the value at the first clock edge
  always_ff @(posedge clk)
    if (en && count != 3'd6)        // the bug: the spec says stop at 5
      count <= count + 3'd1;
  assign q = count;
  always_comb
    AtMostFive_A: assert (count <= 3'd5);
endmodule
