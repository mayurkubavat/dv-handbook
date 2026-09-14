// unique constraint: three 2-bit elements are pairwise distinct
class pkt; rand bit [1:0] x[3]; constraint c { unique {x}; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int n = 0; n < 20; n++) begin
      if (p.randomize() != 1) ok = 0;
      if (p.x[0] == p.x[1] || p.x[1] == p.x[2] || p.x[0] == p.x[2]) ok = 0;
    end
    $display("x=%0d %0d %0d", p.x[0], p.x[1], p.x[2]);
    if (ok) $display("PROBE r13 PASS"); else $display("PROBE r13 FAIL");
    $finish; end
endmodule
