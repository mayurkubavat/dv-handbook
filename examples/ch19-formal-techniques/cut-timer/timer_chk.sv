// timer_chk.sv -- one assertion inside the handshake's timer, attached
// by bind so that the previous chapter's handshake.sv is not edited.
// It is there to show what boxing the timer does to an assertion
// written in the boxed module: the count never exceeds its load.
module timer_chk (
  input logic        clk, rst,
  input logic [15:0] t
);
  Range_A: assert property (@(posedge clk) disable iff (rst)
             t <= 16'd200);
endmodule

bind timer timer_chk u_chk (.clk, .rst, .t);
