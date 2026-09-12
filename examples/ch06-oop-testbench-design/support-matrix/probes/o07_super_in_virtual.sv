// The derived override calls super.f() and adds to it. Through the base
// handle the answer must be base + derived = 10 + 1.
class base; virtual function int f(); return 10; endfunction endclass
class derived extends base;
  virtual function int f(); return super.f() + 1; endfunction endclass
module top; base b; derived d;
  initial begin d = new; b = d;
    $display("via_base=%0d via_derived=%0d", b.f(), d.f());
    if (b.f() == 11 && d.f() == 11) $display("PROBE o07 PASS");
    else $display("PROBE o07 FAIL"); $finish; end
endmodule
