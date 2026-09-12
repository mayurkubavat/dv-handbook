// the base handle is a PROPERTY of another object rather than a module
// variable; dispatch must still follow the object
class base; virtual function int f(); return 1; endfunction endclass
class derived extends base; virtual function int f(); return 2; endfunction
endclass
class holder; base item; endclass
module top; holder h; derived d;
  initial begin h = new; d = new; h.item = d;
    $display("f=%0d", h.item.f());
    if (h.item.f() == 2) $display("PROBE o38 PASS");
    else $display("PROBE o38 FAIL"); $finish; end
endmodule
