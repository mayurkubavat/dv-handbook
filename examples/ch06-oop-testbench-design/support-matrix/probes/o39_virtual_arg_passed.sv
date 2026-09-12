// a derived object passed to a function whose argument is base-typed;
// the virtual call inside that function must reach the derived body
class base; virtual function int f(); return 1; endfunction endclass
class derived extends base; virtual function int f(); return 2; endfunction
endclass
module top; derived d;
  function int call_it(base b); return b.f(); endfunction
  initial begin d = new;
    $display("f=%0d", call_it(d));
    if (call_it(d) == 2) $display("PROBE o39 PASS");
    else $display("PROBE o39 FAIL"); $finish; end
endmodule
