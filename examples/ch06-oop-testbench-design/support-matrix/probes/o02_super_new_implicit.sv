// extends with NO super.new call: the implicit super.new() must run the
// base constructor (default argument) before the derived body.
class base; int id;
  function new(int i = 42); id = i; endfunction endclass
class derived extends base; int extra;
  function new(); extra = id + 1; endfunction endclass
module top; derived d;
  initial begin d = new();
    $display("id=%0d extra=%0d", d.id, d.extra);
    if (d.id == 42 && d.extra == 43) $display("PROBE o02 PASS");
    else $display("PROBE o02 FAIL"); $finish; end
endmodule
