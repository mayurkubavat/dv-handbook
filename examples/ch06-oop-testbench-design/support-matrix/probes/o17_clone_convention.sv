// The copy()/clone() convention: a virtual clone() in the base returns a
// base handle; the derived override builds a derived object and copies its
// own fields too. Through a base handle, clone() must produce a derived
// object with the derived field copied.
class base; int n;
  virtual function void copy(base rhs); n = rhs.n; endfunction
  virtual function base clone(); base p = new; p.copy(this); return p;
  endfunction endclass
class derived extends base; int extra;
  virtual function void copy(base rhs); derived r; super.copy(rhs);
    if ($cast(r, rhs)) extra = r.extra; endfunction
  virtual function base clone(); derived p = new; p.copy(this); return p;
  endfunction endclass
module top; base b, c; derived d, dc; int ok;
  initial begin d = new; d.n = 3; d.extra = 4; b = d; c = b.clone();
    ok = $cast(dc, c);
    $display("ok=%0d n=%0d extra=%0d distinct=%0d", ok, c.n,
             (dc != null) ? dc.extra : -1, (c != b));
    if (ok == 1 && c.n == 3 && dc.extra == 4 && c != b)
      $display("PROBE o17 PASS"); else $display("PROBE o17 FAIL"); $finish; end
endmodule
