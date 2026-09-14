// signed rand int constrained to [-5:5]: negatives must appear
class pkt; rand int v; constraint c { v inside {[-5:5]}; } endclass
module top; pkt p; int ok, nneg;
  initial begin p = new; ok = 1; nneg = 0;
    for (int i = 0; i < 60; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (p.v < -5 || p.v > 5) ok = 0; if (p.v < 0) nneg++; end
    $display("v=%0d nneg=%0d", p.v, nneg);
    if (ok && nneg > 0) $display("PROBE r29 PASS");
    else $display("PROBE r29 FAIL"); $finish; end
endmodule
