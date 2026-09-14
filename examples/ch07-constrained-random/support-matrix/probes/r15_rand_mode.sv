// rand_mode(0) freezes a variable: a keeps 42 while b still randomizes,
// and a.rand_mode() reports 0
class pkt; rand bit [7:0] a, b; endclass
module top; pkt p; int ok, same;
  initial begin p = new; ok = 1; same = 0;
    p.a = 42; p.a.rand_mode(0);
    if (p.a.rand_mode() != 0) ok = 0;
    for (int i = 0; i < 8; i++) begin
      if (p.randomize() != 1) ok = 0; if (p.a != 42) ok = 0; end
    $display("a=%0d b=%0d mode=%0d", p.a, p.b, p.a.rand_mode());
    if (ok) $display("PROBE r15 PASS"); else $display("PROBE r15 FAIL");
    $finish; end
endmodule
