// randomize() with an inline constraint: value stays in the range
class pkt; rand bit [7:0] a; endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int i = 0; i < 20; i++) begin
      if (p.randomize() with { a inside {[10:20]}; } != 1) ok = 0;
      if (p.a < 10 || p.a > 20) ok = 0; end
    $display("last a=%0d", p.a);
    if (ok) $display("PROBE r03 PASS"); else $display("PROBE r03 FAIL");
    $finish; end
endmodule
