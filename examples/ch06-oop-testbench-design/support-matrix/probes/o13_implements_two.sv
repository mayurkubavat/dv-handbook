// one class implements two interface classes; reachable through either
interface class has_id; pure virtual function int id(); endclass
interface class has_len; pure virtual function int len(); endclass
class pkt implements has_id, has_len;
  virtual function int id(); return 7; endfunction
  virtual function int len(); return 64; endfunction endclass
module top; has_id i; has_len l; pkt k;
  initial begin k = new; i = k; l = k;
    $display("id=%0d len=%0d", i.id(), l.len());
    if (i.id() == 7 && l.len() == 64) $display("PROBE o13 PASS");
    else $display("PROBE o13 FAIL"); $finish; end
endmodule
