// inside an array variable: a takes only values held in a non-rand array
class pkt; rand bit [7:0] a; bit [7:0] allowed[3] = '{3, 17, 250};
  constraint c { a inside {allowed}; } endclass
module top; pkt p; int ok;
  initial begin p = new; ok = 1;
    for (int i = 0; i < 30; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (!(p.a == 3 || p.a == 17 || p.a == 250)) ok = 0; end
    $display("a=%0d", p.a);
    if (ok) $display("PROBE r25 PASS"); else $display("PROBE r25 FAIL");
    $finish; end
endmodule
