// A derived class, with the overriding method called through the *derived*
// handle. No dispatch decision is needed, which is what separates this row
// from the one below it.
class shape;
  virtual function int area(); return 0; endfunction
endclass
class square extends shape;
  int side;
  function new(int s); side = s; endfunction
  virtual function int area(); return side * side; endfunction
endclass
module top;
  square sq;
  initial begin
    sq = new(3);
    if (sq.area() == 9) $display("PROBE inherit_derived PASS");
    else $display("PROBE inherit_derived FAIL");
    $finish;
  end
endmodule
