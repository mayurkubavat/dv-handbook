// soft constraint: honored when nothing contradicts it, dropped when an
// inline hard constraint does, and randomize() returns 1 both times
class pkt; rand bit [7:0] a; constraint c { soft a == 5; } endclass
module top; pkt p; int ok, r1, r2; bit [7:0] a1, a2;
  initial begin p = new; ok = 1;
    r1 = p.randomize(); a1 = p.a;
    r2 = p.randomize() with { a == 7; }; a2 = p.a;
    $display("r1=%0d a1=%0d r2=%0d a2=%0d", r1, a1, r2, a2);
    if (r1 == 1 && a1 == 5 && r2 == 1 && a2 == 7) $display("PROBE r12 PASS");
    else $display("PROBE r12 FAIL"); $finish; end
endmodule
