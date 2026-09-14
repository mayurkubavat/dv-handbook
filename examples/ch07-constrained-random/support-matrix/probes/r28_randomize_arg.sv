// randomize(a): only the named variable changes; b keeps its value
class pkt; rand bit [7:0] a, b; endclass
module top; pkt p; int ok, sameA;
  initial begin p = new; ok = 1; sameA = 0; p.b = 99; p.a = 0;
    for (int i = 0; i < 8; i++) begin
      if (p.randomize(a) != 1) ok = 0;
      if (p.b != 99) ok = 0; if (p.a == 0) sameA++; end
    $display("a=%0d b=%0d sameA=%0d", p.a, p.b, sameA);
    if (ok && sameA < 8) $display("PROBE r28 PASS");
    else $display("PROBE r28 FAIL"); $finish; end
endmodule
