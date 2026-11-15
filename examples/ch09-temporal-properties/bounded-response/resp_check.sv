// resp_check.sv -- "a grant within three ticks of every request".
//
// The rule spans four ticks, so the checker carries the state the rule
// needs as ordinary registers: waiting[i] says that a request i+1
// ticks old has seen no grant yet. The assertion is then a condition
// on one tick: the oldest waiting request is not left without a grant.
// Nothing here is beyond a clocked block and an immediate assertion.
module resp_check (
  input logic clk,
  input logic rst_n,
  input logic req,
  input logic gnt
);
  logic [2:0] waiting;
  always @(posedge clk)
    if (!rst_n)   waiting <= '0;
    else if (gnt) waiting <= {2'b00, req};        // a grant serves all
    else          waiting <= {waiting[1:0], req}; // everyone ages

  always @(posedge clk) if (rst_n) begin
    Window_A: assert (!(waiting[2] && !gnt));
    Waited_C: cover (waiting[2] && gnt);   // a grant at the last tick
  end
endmodule
