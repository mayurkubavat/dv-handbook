class shape; virtual function int area(); return 0; endfunction endclass
class square extends shape; int side;
  function new(int s); side = s; endfunction
  virtual function int area(); return side * side; endfunction endclass
module top; shape s; square sq;
  initial begin sq = new(3); s = sq;
    $display("direct=%0d via_base=%0d", sq.area(), s.area());
    if (sq.area()==9 && s.area()==9) $display("PROBE j15a PASS"); else $display("PROBE j15a FAIL"); $finish; end
endmodule
