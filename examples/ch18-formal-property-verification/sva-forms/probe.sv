// probe.sv -- a design small enough that the truth of each probe can
// be read off it.
//
//   d1, d2, d3   the input a one, two and three cycles ago (no reset)
//   c            a three-bit counter that runs free and wraps
//   q            counts up to LIM while en is high, and stays there
//   done         q has reached LIM
//   u_leaf.hid   a register in an instance below: the same as d1
module leaf (
  input  logic clk,
  input  logic d,
  output logic q
);
  logic hid;
  always_ff @(posedge clk) hid <= d;
  assign q = hid;
endmodule

module probe #(parameter logic [3:0] LIM = 4'd9) (
  input  logic       clk,
  input  logic       rst,
  input  logic       en,
  input  logic       a,
  input  logic       b,
  output logic [3:0] q,
  output logic       done,
  output logic       y
);
  logic       d1, d2, d3;
  logic [2:0] c;
  always_ff @(posedge clk) begin
    d1 <= a;
    d2 <= d1;
    d3 <= d2;
    if (rst) begin
      q <= '0;
      c <= '0;
    end else begin
      c <= c + 3'd1;
      if (en && q != LIM) q <= q + 4'd1;
    end
  end
  assign done = (q == LIM);
  leaf u_leaf (.clk, .d(a), .q(y));
endmodule
