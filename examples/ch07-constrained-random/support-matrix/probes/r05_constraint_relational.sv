// two variables related by a constraint: a < b < 50, checked every call
class pkt; rand bit [7:0] a, b; constraint c { a < b; b < 50; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int i = 0; i < 40; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (!(p.a < p.b && p.b < 50)) ok = 0; end
    $display("last a=%0d b=%0d", p.a, p.b);
    if (ok) $display("PROBE r05 PASS"); else $display("PROBE r05 FAIL");
    $finish; end
endmodule
