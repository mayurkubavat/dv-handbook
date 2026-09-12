// the derived override omits the `virtual` keyword; it is still virtual
// because the base declared it so
class base; virtual function int f(); return 1; endfunction endclass
class derived extends base; function int f(); return 2; endfunction endclass
module top; base b; derived d;
  initial begin d = new; b = d;
    $display("via_base=%0d", b.f());
    if (b.f() == 2) $display("PROBE o27 PASS");
    else $display("PROBE o27 FAIL"); $finish; end
endmodule
