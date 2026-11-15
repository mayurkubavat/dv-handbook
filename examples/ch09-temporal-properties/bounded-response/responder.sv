// responder.sv -- answers every request with a grant: one tick later,
// or three ticks later when the request is marked slow. The contract
// is "a grant within three ticks of every request". SLOW_BY_ONE builds
// the version whose slow path takes four.
module responder #(parameter bit SLOW_BY_ONE = 0) (
  input  logic clk,
  input  logic rst_n,
  input  logic req,
  input  logic slow,
  output logic gnt
);
  logic       fast_q;                  // a fast request, one tick old
  logic [3:0] slow_q;                  // slow requests, by age
  always_ff @(posedge clk)
    if (!rst_n) begin
      fast_q <= 1'b0;
      slow_q <= '0;
    end else begin
      fast_q <= req && !slow;
      slow_q <= {slow_q[2:0], req && slow};
    end
  assign gnt = fast_q || (SLOW_BY_ONE ? slow_q[3] : slow_q[2]);
endmodule
