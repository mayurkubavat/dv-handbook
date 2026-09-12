// Three levels a <- b <- c, all overriding. A handle of the ROOT type
// holding a c must run c's body; a handle of the MIDDLE type holding a c
// must also run c's body. A tool that dispatches on the declared type of
// the handle gives 1 and 2 instead of 3 and 3.
class a; virtual function int f(); return 1; endfunction endclass
class b extends a; virtual function int f(); return 2; endfunction endclass
class c extends b; virtual function int f(); return 3; endfunction endclass
module top; a ha; b hb; c hc;
  initial begin hc = new; hb = hc; ha = hc;
    $display("via_a=%0d via_b=%0d via_c=%0d", ha.f(), hb.f(), hc.f());
    if (ha.f() == 3 && hb.f() == 3 && hc.f() == 3) $display("PROBE o08 PASS");
    else $display("PROBE o08 FAIL"); $finish; end
endmodule
