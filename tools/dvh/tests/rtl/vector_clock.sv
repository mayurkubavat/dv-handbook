// One clock *port* carrying two unrelated clocks, one per bit. Every bit of
// a vector port has the same name, so a check that compares source names
// sees one clock here and excuses the crossing below. Identity is the net.
module vector_clock (
    input  logic [1:0] lane_clk,
    input  logic [7:0] din,
    output logic [7:0] dout
);
  logic [7:0] stage;

  always_ff @(posedge lane_clk[0])
    stage <= din;

  always_ff @(posedge lane_clk[1])
    dout <= stage;             // eight bits, no synchronizer
endmodule
