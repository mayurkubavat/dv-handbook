// a class extending a specialization of a parameterized base; the base's
// parameter shapes the derived object and a virtual call still dispatches
class base #(int W = 8); bit [W-1:0] d;
  virtual function int width(); return $bits(d); endfunction endclass
class narrow extends base #(4);
  virtual function int width(); return super.width() * 10; endfunction
endclass
module top; base #(4) b; narrow n;
  initial begin n = new; b = n;
    $display("w=%0d via_base=%0d", n.width(), b.width());
    if (n.width() == 40 && b.width() == 40) $display("PROBE o21 PASS");
    else $display("PROBE o21 FAIL"); $finish; end
endmodule
