// extends with the constructor arguments carried by the extends clause
class base; int id;
  function new(int i); id = i; endfunction endclass
class derived extends base(7); int extra;
  function new(); extra = 3; endfunction endclass
module top; derived d;
  initial begin d = new;
    $display("id=%0d extra=%0d", d.id, d.extra);
    if (d.id == 7 && d.extra == 3) $display("PROBE o42 PASS");
    else $display("PROBE o42 FAIL"); $finish; end
endmodule
