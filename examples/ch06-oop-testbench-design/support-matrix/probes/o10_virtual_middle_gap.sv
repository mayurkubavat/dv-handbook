// a <- b <- c where only a and c override: through an a handle holding a c
// the answer is c's; through an a handle holding a b it is a's (inherited).
class a; virtual function int f(); return 1; endfunction endclass
class b extends a; endclass
class c extends b; virtual function int f(); return 3; endfunction endclass
module top; a ha1, ha2; b hb; c hc;
  initial begin hc = new; hb = new; ha1 = hc; ha2 = hb;
    $display("a_holding_c=%0d a_holding_b=%0d", ha1.f(), ha2.f());
    if (ha1.f() == 3 && ha2.f() == 1) $display("PROBE o10 PASS");
    else $display("PROBE o10 FAIL"); $finish; end
endmodule
