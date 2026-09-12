// virtual void function that sets a property, through a base handle
class base; int v;
  virtual function void set(); v = 1; endfunction endclass
class derived extends base;
  virtual function void set(); v = 2; endfunction endclass
module top; base b; derived d;
  initial begin d = new; b = d; b.set();
    $display("v=%0d", b.v);
    if (b.v == 2) $display("PROBE o06 PASS");
    else $display("PROBE o06 FAIL"); $finish; end
endmodule
