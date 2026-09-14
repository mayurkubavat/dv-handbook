// dist with :/ weights: [0:3] :/ 1 shares one unit over four values, 9 := 9
// gets nine units; only listed values appear and 9 dominates over 200 calls
class pkt; rand bit [3:0] a; constraint c { a dist { [0:3] :/ 1, 9 := 9 }; }
endclass
module top; pkt p; int ok, nlow, n9;
  initial begin p = new; ok = 1; nlow = 0; n9 = 0;
    for (int i = 0; i < 200; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (p.a <= 3) nlow++; else if (p.a == 9) n9++; else ok = 0; end
    $display("nlow=%0d n9=%0d", nlow, n9);
    if (ok && n9 > nlow) $display("PROBE r07 PASS");
    else $display("PROBE r07 FAIL"); $finish; end
endmodule
