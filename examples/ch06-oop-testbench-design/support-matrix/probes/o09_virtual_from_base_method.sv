// Template-method shape: a NON-virtual base method run() calls a virtual
// step(). Calling run() on the DERIVED handle must still reach the derived
// step(), because dispatch depends on the object, not on where the call is.
class base;
  virtual function int step(); return 1; endfunction
  function int run(); return step() * 100; endfunction endclass
class derived extends base;
  virtual function int step(); return 2; endfunction endclass
module top; base b; derived d;
  initial begin d = new; b = d;
    $display("run_via_derived=%0d run_via_base=%0d", d.run(), b.run());
    if (d.run() == 200 && b.run() == 200) $display("PROBE o09 PASS");
    else $display("PROBE o09 FAIL"); $finish; end
endmodule
