// contradictory constraints: randomize() must return 0, not 1
class pkt; rand bit [7:0] a; constraint c { a > 5; a < 3; } endclass
module top; pkt p; int r;
  initial begin p = new; p.a = 77; r = p.randomize();
    $display("r=%0d a=%0d", r, p.a);
    if (r == 0) $display("PROBE r24 PASS"); else $display("PROBE r24 FAIL");
    $finish; end
endmodule
