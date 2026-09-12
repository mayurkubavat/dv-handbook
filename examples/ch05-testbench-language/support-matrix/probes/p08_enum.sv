// enums and their methods
module top;
  typedef enum logic [1:0] { IDLE, BUSY, DONE } state_t;
  state_t s; int n;
  initial begin
    s = IDLE; n = 0;
    $display("first=%s num=%0d", s.name(), s.num());
    s = s.next(); $display("next=%s (%0d)", s.name(), s);
    s = state_t'(2); $display("cast=%s", s.name());
    if (s == DONE && s.name() == "DONE") $display("PROBE p08 PASS");
    else $display("PROBE p08 FAIL");
    $finish;
  end
endmodule
