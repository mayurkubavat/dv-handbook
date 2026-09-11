// Two one-bit chains carrying one two-bit value, one sender clocked by
// aclk and the other by aclk through a black-box clock buffer. The netlist
// cannot know the buffer's output is aclk, so it cannot show the two chains
// cross different boundaries either; their groups are merged.
(* blackbox *)
module CLKBUF (input logic I, output logic O);
endmodule

module per_bit_buffered_clock (input logic aclk, bclk, input logic d0, d1,
                 output logic o0, o1);
  logic aclk_b, a0, a1, p0, p1, r0, r1;
  CLKBUF u_buf (.I(aclk), .O(aclk_b));
  always_ff @(posedge aclk)   a0 <= d0;
  always_ff @(posedge aclk_b) a1 <= d1;
  always_ff @(posedge bclk) begin p0 <= a0; p1 <= a1; end
  always_ff @(posedge bclk) begin r0 <= p0; r1 <= p1; end
  assign o0 = r0;
  assign o1 = r1;
endmodule
