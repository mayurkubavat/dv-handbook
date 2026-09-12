// factory pattern: a static function selects the derived type by a string
// key and returns a base handle
typedef class d1; typedef class d2;
class base; virtual function int f(); return 0; endfunction
  static function base make(string kind);
    d1 x; d2 y;
    if (kind == "one") begin x = new; return x; end
    else begin y = new; return y; end
  endfunction endclass
class d1 extends base; virtual function int f(); return 1; endfunction endclass
class d2 extends base; virtual function int f(); return 2; endfunction endclass
module top; base p, q;
  initial begin p = base::make("one"); q = base::make("two");
    $display("p=%0d q=%0d", p.f(), q.f());
    if (p.f() == 1 && q.f() == 2) $display("PROBE o30 PASS");
    else $display("PROBE o30 FAIL"); $finish; end
endmodule
