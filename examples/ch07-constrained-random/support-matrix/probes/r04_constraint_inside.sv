// constraint block with inside: value stays in the set
class pkt; rand bit [7:0] a;
  constraint c { a inside {[10:20], 100, [200:210]}; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int i = 0; i < 40; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (!(p.a inside {[10:20], 100, [200:210]})) ok = 0; end
    $display("last a=%0d", p.a);
    if (ok) $display("PROBE r04 PASS"); else $display("PROBE r04 FAIL");
    $finish; end
endmodule
