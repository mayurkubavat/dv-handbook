// The ordinary asynchronous set/reset flip-flop. Yosys builds its SET and
// CLR nets out of multiplexers whose *select* carries the reset signal, and
// the reset walk was the clock walk -- which skips a multiplexer's select,
// because a select is not a clock. So the reported reset source was a pair
// of constants and neither `r` nor `s` was ever named.
module set_reset_flop (
    input  logic clk,
    input  logic s,
    input  logic r,
    input  logic d,
    output logic q
);
  logic v;

  always_ff @(posedge clk or posedge s or posedge r)
    if (r)      v <= 1'b0;
    else if (s) v <= 1'b1;
    else        v <= d;

  assign q = v;
endmodule
