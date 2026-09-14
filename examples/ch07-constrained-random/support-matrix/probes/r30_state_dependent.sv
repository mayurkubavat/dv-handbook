// constraint referring to a non-rand state variable: a < limit, with
// limit changed between calls
class pkt; rand bit [7:0] a; bit [7:0] limit;
  constraint c { a < limit; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    p.limit = 4;
    for (int i = 0; i < 10; i++) begin
      if (p.randomize() != 1) ok = 0; if (p.a >= 4) ok = 0; end
    p.limit = 200;
    for (int i = 0; i < 10; i++) begin
      if (p.randomize() != 1) ok = 0; if (p.a >= 200) ok = 0; end
    $display("a=%0d", p.a);
    if (ok) $display("PROBE r30 PASS"); else $display("PROBE r30 FAIL");
    $finish; end
endmodule
