// rand class-handle member: randomizing the parent randomizes the child
// under the child's own constraint
class sub; rand bit [7:0] x; constraint c { x inside {[1:4]}; } endclass
class pkt; rand sub s; rand bit [7:0] y; constraint c { y > 100; }
  function new(); s = new; endfunction endclass
module top; pkt p; int ok, same; bit [7:0] x0;
  initial begin p = new; ok = 1; same = 0;
    for (int i = 0; i < 20; i++) begin
      if (p.randomize() != 1) ok = 0;
      if (!(p.s.x inside {[1:4]}) || !(p.y > 100)) ok = 0;
      if (i == 0) x0 = p.s.x; else if (p.s.x == x0) same++; end
    $display("x=%0d y=%0d same=%0d", p.s.x, p.y, same);
    if (ok && same < 19) $display("PROBE r27 PASS");
    else $display("PROBE r27 FAIL"); $finish; end
endmodule
