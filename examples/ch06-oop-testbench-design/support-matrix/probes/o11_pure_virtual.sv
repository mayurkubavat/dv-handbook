// virtual (abstract) class with a pure virtual method; concrete subclass
// called through the abstract handle
virtual class shape; pure virtual function int area(); endclass
class square extends shape; int s;
  function new(int side); s = side; endfunction
  virtual function int area(); return s * s; endfunction endclass
module top; shape sh; square sq;
  initial begin sq = new(4); sh = sq;
    $display("area=%0d", sh.area());
    if (sh.area() == 16) $display("PROBE o11 PASS");
    else $display("PROBE o11 FAIL"); $finish; end
endmodule
