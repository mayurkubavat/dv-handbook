// tb_cast_clone.sv -- casting down a hierarchy, and copying across it.
//
// Assigning a derived handle to a base handle needs no cast. Going the
// other way is a question the compiler cannot answer, so `$cast` asks it
// at run time and says no by returning zero. Copying is the other trap:
// `new src` copies the *declared* type of the handle it is given, which on
// the simulator this book measures builds a base object from a derived
// one. A copy that keeps its type is a virtual method that constructs its
// own class, which is what `clone` is here.
class packet;
  int id;
  function new(int id_ = 0); id = id_; endfunction
  virtual function string tag(); return "packet"; endfunction
  virtual function packet clone();
    packet p = new(id);
    return p;
  endfunction
endclass
class error_packet extends packet;
  int code;
  function new(int id_ = 0, int code_ = 0); super.new(id_); code = code_;
  endfunction
  virtual function string tag(); return "error_packet"; endfunction
  virtual function packet clone();
    error_packet e = new(id, code);
    return e;
  endfunction
endclass

module tb_cast_clone;
  packet       base, plain, copy_by_new, copy_by_clone;
  error_packet err, back;
  int ok;
  initial begin
    err = new(1, 500);
    base = err;                          // up: implicit
    ok = $cast(back, base);              // down: checked, succeeds
    $display("$cast(back, base) -> %0d; back.code=%0d", ok, back.code);
    plain = new(2);
    ok = $cast(back, plain);             // down: checked, refused
    $display("$cast(back, plain) -> %0d; back still names id=%0d", ok,
             back.id);
    copy_by_new   = new base;            // copies the handle's declared type
    copy_by_clone = base.clone();        // constructs the object's own type
    $display("new base       -> tag %s", copy_by_new.tag());
    $display("base.clone()   -> tag %s", copy_by_clone.tag());
    $finish;
  end
endmodule
