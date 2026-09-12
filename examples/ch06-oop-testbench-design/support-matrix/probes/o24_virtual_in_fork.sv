// virtual calls made from inside fork branches, on two base handles that
// hold different derived types; both must dispatch to their own override
class base; virtual function int f(); return 0; endfunction endclass
class d1 extends base; virtual function int f(); return 1; endfunction endclass
class d2 extends base; virtual function int f(); return 2; endfunction endclass
module top; base h1, h2; d1 x; d2 y; int r1, r2;
  initial begin x = new; y = new; h1 = x; h2 = y;
    fork
      begin #1 r1 = h1.f(); end
      begin #2 r2 = h2.f(); end
    join
    $display("r1=%0d r2=%0d", r1, r2);
    if (r1 == 1 && r2 == 2) $display("PROBE o24 PASS");
    else $display("PROBE o24 FAIL"); $finish; end
endmodule
