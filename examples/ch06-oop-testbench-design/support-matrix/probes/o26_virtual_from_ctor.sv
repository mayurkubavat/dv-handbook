// a virtual method called from the BASE constructor, overridden in the
// derived class. The object is of the derived type from the start, so the
// derived body runs; but the derived property initializers have not run
// yet when it does, so the value it reads is the default 0, not 5.
class base; int seen;
  function new(); seen = kind(); endfunction
  virtual function int kind(); return 1; endfunction endclass
class derived extends base; int k = 5;
  virtual function int kind(); return 100 + k; endfunction endclass
module top; derived d;
  initial begin d = new;
    $display("seen=%0d", d.seen);
    if (d.seen == 100) $display("PROBE o26 PASS");
    else $display("PROBE o26 FAIL"); $finish; end
endmodule
