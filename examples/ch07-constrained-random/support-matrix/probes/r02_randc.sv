// randc: a 2-bit cyclic variable yields each of its four values exactly
// once per cycle of four calls, for two cycles
class pkt; randc bit [1:0] c; endclass
module top; pkt p; int seen[4]; int ok;
  initial begin p = new; ok = 1;
    for (int cyc = 0; cyc < 2; cyc++) begin
      for (int i = 0; i < 4; i++) seen[i] = 0;
      for (int i = 0; i < 4; i++) begin
        if (p.randomize() != 1) ok = 0; seen[p.c]++; end
      for (int i = 0; i < 4; i++) if (seen[i] != 1) ok = 0;
      $display("cycle %0d: %0d %0d %0d %0d", cyc, seen[0], seen[1],
               seen[2], seen[3]);
    end
    if (ok) $display("PROBE r02 PASS"); else $display("PROBE r02 FAIL");
    $finish; end
endmodule
