// A latch with an asynchronous clear driven from another domain's
// register. A hand-written list of the latch's data pins missed the clear
// pin, and the same clear on a flip-flop was reported.
module latch_async_clear (input logic aclk, bclk, input logic [7:0] d,
                          input logic e, 
                output logic [7:0] q);
  logic [7:0] da;
  logic en, clr;
  always_ff @(posedge aclk) begin da <= d; en <= e; end
  always_ff @(posedge bclk) clr <= ~e;
  always_latch if (clr) q <= '0; else if (en) q <= da;
  // q is captured under aclk timing, cleared under bclk timing
endmodule
