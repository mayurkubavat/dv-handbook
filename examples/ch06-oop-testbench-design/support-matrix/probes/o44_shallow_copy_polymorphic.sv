// shallow copy `new src` through a BASE handle that holds a derived
// object: the copy must have the source object's runtime type, so a
// virtual call on the copy reaches the derived body
class base; virtual function int f(); return 1; endfunction endclass
class derived extends base; virtual function int f(); return 2; endfunction
endclass
module top; base b, c; derived d;
  initial begin d = new; b = d; c = new b;
    $display("copy_f=%0d", c.f());
    if (c.f() == 2) $display("PROBE o44 PASS");
    else $display("PROBE o44 FAIL"); $finish; end
endmodule
