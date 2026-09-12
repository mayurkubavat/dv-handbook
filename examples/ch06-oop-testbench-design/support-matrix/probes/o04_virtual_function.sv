// virtual int-returning function through a base handle: derived body expected
class base; virtual function int f(); return 1; endfunction endclass
class derived extends base;
  virtual function int f(); return 2; endfunction endclass
module top; base b; derived d;
  initial begin d = new; b = d;
    $display("via_base=%0d via_derived=%0d", b.f(), d.f());
    if (b.f() == 2 && d.f() == 2) $display("PROBE o04 PASS");
    else $display("PROBE o04 FAIL"); $finish; end
endmodule
