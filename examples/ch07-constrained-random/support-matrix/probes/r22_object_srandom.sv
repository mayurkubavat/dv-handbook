// object stability: two objects seeded with the same srandom() value
// produce the same sequence; a third seeded differently need not
class pkt; rand bit [31:0] a; endclass
module top; pkt p, q; int ok; bit [31:0] pa[4], qa[4];
  initial begin p = new; q = new; ok = 1;
    p.srandom(7); q.srandom(7);
    for (int i = 0; i < 4; i++) begin
      if (p.randomize() != 1) ok = 0; pa[i] = p.a;
      if (q.randomize() != 1) ok = 0; qa[i] = q.a; end
    for (int i = 0; i < 4; i++) if (pa[i] != qa[i]) ok = 0;
    $display("pa[0]=%0d qa[0]=%0d", pa[0], qa[0]);
    if (ok) $display("PROBE r22 PASS"); else $display("PROBE r22 FAIL");
    $finish; end
endmodule
