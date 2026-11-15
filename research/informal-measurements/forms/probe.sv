module leaf(input logic clk, input logic rst, input logic d, output logic q);
  logic hid;
  always_ff @(posedge clk) if (rst) hid <= 1'b0; else hid <= d;
  assign q = hid;
endmodule
module probe #(parameter int W = 4, parameter logic [3:0] LIM = 4'd9)
  (input logic clk, input logic rst, input logic en, input logic a, input logic b,
   output logic [W-1:0] q, output logic done);
  logic y;
  always_ff @(posedge clk)
    if (rst) q <= '0;
    else if (en && q != LIM) q <= q + 1'b1;
  assign done = q == LIM;
  leaf u_leaf(.clk, .rst, .d(a), .q(y));
endmodule
