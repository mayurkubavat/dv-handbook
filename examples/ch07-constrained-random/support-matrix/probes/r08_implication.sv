// implication: mode selects the range of a; both modes must occur
class pkt; rand bit mode; rand bit [7:0] a;
  constraint c { mode == 1 -> a > 200; mode == 0 -> a < 10; } endclass
module top; pkt p; int ok, m0, m1;
  initial begin p = new; ok = 1; m0 = 0; m1 = 0;
    for (int i = 0; i < 40; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (p.mode) begin m1++; if (!(p.a > 200)) ok = 0; end
      else begin m0++; if (!(p.a < 10)) ok = 0; end end
    $display("m0=%0d m1=%0d", m0, m1);
    if (ok && m0 > 0 && m1 > 0) $display("PROBE r08 PASS");
    else $display("PROBE r08 FAIL"); $finish; end
endmodule
