// resp_check.sv -- "a grant within three ticks of every request".
//
// The rule spans four ticks, so the checker carries the state the rule
// needs as ordinary registers: waiting[i] says that a request i+1
// ticks old has seen no grant yet. The property is then a condition
// on one tick: the oldest waiting request is not left without a grant.
module resp_check (
  input logic clk,
  input logic rst_n,
  input logic req,
  input logic gnt
);
  logic [2:0] waiting;
  always_ff @(posedge clk)
    if (!rst_n)   waiting <= '0;
    else if (gnt) waiting <= {2'b00, req};        // a grant serves all
    else          waiting <= {waiting[1:0], req}; // everyone ages

  Window_A: assert property (@(posedge clk) disable iff (!rst_n)
              !(waiting[2] && !gnt));
  // A grant at the last permitted tick.
  Waited_C: cover property (@(posedge clk) disable iff (!rst_n)
              waiting[2] && gnt);
endmodule
