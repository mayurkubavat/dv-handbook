// dist with := weights: only listed values appear, and over 200 calls the
// value with weight 9 appears more often than the value with weight 1
class pkt; rand bit [3:0] a; constraint c { a dist { 2 := 1, 7 := 9 }; }
endclass
module top; pkt p; int ok, n2, n7;
  initial begin p = new; ok = 1; n2 = 0; n7 = 0;
    for (int i = 0; i < 200; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (p.a == 2) n2++; else if (p.a == 7) n7++; else ok = 0; end
    $display("n2=%0d n7=%0d", n2, n7);
    if (ok && n7 > n2) $display("PROBE r06 PASS");
    else $display("PROBE r06 FAIL"); $finish; end
endmodule
