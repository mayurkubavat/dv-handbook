// rand properties, unconstrained randomize(): returns 1 and the values
// are not all the same across eight calls
class pkt; rand bit [7:0] a; rand bit [7:0] b; endclass
module top; pkt p; int ok, same; bit [7:0] a0, b0;
  initial begin p = new; ok = 1; same = 0;
    for (int i = 0; i < 8; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (i == 0) begin a0 = p.a; b0 = p.b; end
      else if (p.a == a0 && p.b == b0) same++;
      $display("a=%0d b=%0d", p.a, p.b);
    end
    if (ok && same < 7) $display("PROBE r01 PASS");
    else $display("PROBE r01 FAIL"); $finish; end
endmodule
