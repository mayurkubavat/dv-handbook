// clone() as a virtual method that constructs its own class, checked
// through virtual methods only: no $cast and no handle comparison, so a
// refusal or a wrong answer here is about clone and nothing beside it.
class base;
  int n;
  function new(int n_ = 0); n = n_; endfunction
  virtual function string tag(); return "base"; endfunction
  virtual function base clone(); base b = new(n); return b; endfunction
endclass
class derived extends base;
  function new(int n_ = 0); super.new(n_); endfunction
  virtual function string tag(); return "derived"; endfunction
  virtual function base clone(); derived d = new(n); return d; endfunction
endclass
module top;
  base b, c; derived d;
  initial begin
    d = new(3); b = d;
    c = b.clone();
    if (c.tag() == "derived" && c.n == 3) $display("PROBE o17 PASS");
    else $display("PROBE o17 FAIL");
    $finish;
  end
endmodule
