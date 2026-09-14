// constraint_mode(0) turns a constraint off: a == 5 is enforced, then
// disabled, and 20 calls no longer all give 5; the query returns 0
class pkt; rand bit [7:0] a; constraint c { a == 5; } endclass
module top; pkt p; int ok, n5;
  initial begin p = new; ok = 1; n5 = 0;
    if (p.randomize() != 1 || p.a != 5) ok = 0;
    p.c.constraint_mode(0);
    if (p.c.constraint_mode() != 0) ok = 0;
    for (int i = 0; i < 20; i++) begin
      if (p.randomize() != 1) ok = 0; if (p.a == 5) n5++; end
    $display("n5=%0d mode=%0d", n5, p.c.constraint_mode());
    if (ok && n5 < 20) $display("PROBE r14 PASS");
    else $display("PROBE r14 FAIL"); $finish; end
endmodule
