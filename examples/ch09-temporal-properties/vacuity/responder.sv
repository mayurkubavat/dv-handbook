// responder.sv -- meant to acknowledge every request one tick later.
// It is broken: it never acknowledges.
module responder (
  input  logic clk,
  input  logic req,
  output logic ack
);
  always_ff @(posedge clk) ack <= 1'b0 & req;    // the bug
  ack_check chk (.*);
endmodule
