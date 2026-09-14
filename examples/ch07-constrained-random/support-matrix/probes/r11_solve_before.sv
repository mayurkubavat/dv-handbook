// solve before: legality only. s -> v == 0, s solved first. Every result
// must satisfy the implication; the distribution is counted in the note.
class pkt; rand bit s; rand bit [7:0] v;
  constraint c { s -> v == 0; solve s before v; } endclass
module top; pkt p; int ok, ns;
  initial begin p = new; ok = 1; ns = 0;
    for (int i = 0; i < 100; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (p.s) begin ns++; if (p.v != 0) ok = 0; end end
    $display("s set %0d of 100", ns);
    if (ok) $display("PROBE r11 PASS"); else $display("PROBE r11 FAIL");
    $finish; end
endmodule
