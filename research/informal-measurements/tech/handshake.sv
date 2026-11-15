// A request/grant block with a slow path: used for assumptions, cut
// points, black boxes and liveness.
module timer #(parameter int N = 200) (input logic clk, input logic rst, input logic start, output logic expired);
  logic [15:0] t;
  always_ff @(posedge clk)
    if (rst) t <= '0;
    else if (start) t <= 16'(N);
    else if (t != 0) t <= t - 16'd1;
  assign expired = (t == 16'd1);
endmodule
module handshake (input logic clk, input logic rst, input logic req, input logic [3:0] d,
                  output logic gnt, output logic busy, output logic [3:0] q);
  logic expired;
  timer #(.N(200)) u_timer (.clk, .rst, .start(req && !busy), .expired);
  always_ff @(posedge clk)
    if (rst) begin busy <= 1'b0; gnt <= 1'b0; q <= '0; end
    else begin
      gnt <= 1'b0;
      if (req && !busy) begin busy <= 1'b1; q <= d; end
      else if (busy && expired) begin busy <= 1'b0; gnt <= 1'b1; end
    end
endmodule
