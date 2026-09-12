// interface class, one class implements it, call through the interface
// class handle
interface class printable; pure virtual function int id(); endclass
class pkt implements printable; int n;
  function new(int v); n = v; endfunction
  virtual function int id(); return n; endfunction endclass
module top; printable p; pkt k;
  initial begin k = new(5); p = k;
    $display("id=%0d", p.id());
    if (p.id() == 5) $display("PROBE o12 PASS");
    else $display("PROBE o12 FAIL"); $finish; end
endmodule
