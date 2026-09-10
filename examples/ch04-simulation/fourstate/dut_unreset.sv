// dut_unreset.sv -- a register nobody resets, read two ways.
//
// `state` has no reset, so under four-state simulation it is unknown until
// something writes it. What each reader then does with that unknown is the
// mechanism Chapter 3 named and did not explain.
//
// `out_bare` is written under a bare `if`: an unknown condition takes
// neither branch, so it simply keeps its previous value.
//
// `out_else` is written under an `if ... else`: an unknown condition runs
// the *else* branch, exactly as though the condition had been false. That
// is the dangerous case, because the design proceeds down a definite path
// chosen by a value nobody knows, and the result looks like an ordinary
// answer rather than like a missing reset.
module dut_unreset (
  input  logic       clk,
  input  logic       go,
  output logic [7:0] out_bare,
  output logic [7:0] out_else
);
  logic [7:0] state;          // deliberately never reset

  always_ff @(posedge clk)
    if (go) state <= state + 8'd1;

  always_ff @(posedge clk)
    if (state != 8'h00) out_bare <= state;

  always_ff @(posedge clk)
    if (state != 8'h00) out_else <= state;
    else                out_else <= 8'hEE;
endmodule
