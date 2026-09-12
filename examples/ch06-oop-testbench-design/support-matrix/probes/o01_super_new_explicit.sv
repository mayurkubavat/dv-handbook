// extends with an explicit super.new(args) chain
class base; int id;
  function new(int i); id = i; endfunction endclass
class derived extends base; int extra;
  function new(int i, int e); super.new(i); extra = e; endfunction endclass
module top; derived d;
  initial begin d = new(7, 3);
    $display("id=%0d extra=%0d", d.id, d.extra);
    if (d.id == 7 && d.extra == 3) $display("PROBE o01 PASS");
    else $display("PROBE o01 FAIL"); $finish; end
endmodule
