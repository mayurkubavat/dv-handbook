// An interface class implemented by a class, called through the
// interface-class handle. Nothing else is declared.
interface class shape;
  pure virtual function int area();
endclass
class square implements shape;
  int side;
  function new(int s); side = s; endfunction
  virtual function int area(); return side * side; endfunction
endclass
module top;
  shape s; square sq;
  initial begin
    sq = new(4); s = sq;
    if (s.area() == 16) $display("PROBE iface_class PASS");
    else $display("PROBE iface_class FAIL");
    $finish;
  end
endmodule
