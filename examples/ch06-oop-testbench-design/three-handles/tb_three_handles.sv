// tb_three_handles.sv -- one object, three handles, one question.
//
// `c` is a leaf object. `a` and `b` name the same object through handles
// declared as its ancestors. The method is virtual, so the language says
// all three calls run the leaf's body: a call dispatches on the object,
// not on the declaration of the handle it came through. A simulator that
// accepts the word `virtual` and ignores it answers three different ways,
// and says nothing.
class shape;
  virtual function int sides(); return 0; endfunction
endclass
class polygon extends shape;
  virtual function int sides(); return 99; endfunction
endclass
class triangle extends polygon;
  virtual function int sides(); return 3; endfunction
endclass

module tb_three_handles;
  shape    a;
  polygon  b;
  triangle c;
  initial begin
    c = new;
    b = c;                 // up-casts are implicit
    a = c;
    $display("sides via a=%0d b=%0d c=%0d  (one object, three handles)",
             a.sides(), b.sides(), c.sides());
    $finish;
  end
endmodule
