// A NON-virtual method redefined in the derived class hides the base one.
// Through a base handle the BASE body runs; through the derived handle the
// derived body runs. Both are what the standard says.
class base; function int f(); return 1; endfunction endclass
class derived extends base; function int f(); return 2; endfunction endclass
module top; base b; derived d;
  initial begin d = new; b = d;
    $display("via_base=%0d via_derived=%0d", b.f(), d.f());
    if (b.f() == 1 && d.f() == 2) $display("PROBE o03 PASS");
    else $display("PROBE o03 FAIL"); $finish; end
endmodule
