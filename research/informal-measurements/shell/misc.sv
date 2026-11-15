module misc(input logic clk, input logic rst, input logic [3:0] d, output logic [3:0] q);
  logic [3:0] k;
  assign k = $anyconst;
  always_ff @(posedge clk) if (rst) q <= '0; else q <= d;
  a_k: assert property (@(posedge clk) $stable(k));
endmodule
