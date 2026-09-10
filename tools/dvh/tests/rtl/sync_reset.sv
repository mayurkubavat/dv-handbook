// sync_reset.sv -- a register with a synchronous reset.
//
// `proc` turns this into a plain flip-flop with a multiplexer in front,
// not a flip-flop with a reset pin. Without a later pass to recognise the
// pattern, the reset tree reports this register as having no reset, which
// is the one finding of that report a reader acts on.
module sync_reset (
  input  logic clk,
  input  logic rst,
  input  logic d,
  output logic q
);
  always_ff @(posedge clk)
    if (rst) q <= 1'b0;
    else     q <= d;
endmodule
