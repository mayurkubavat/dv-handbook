// callback pattern: a driver holds a base-typed hook object with a virtual
// method; the test installs a derived hook and the driver's call reaches it
class hook; virtual function int on_send(int v); return v; endfunction
endclass
class driver; hook cb;
  function int send(int v); return (cb != null) ? cb.on_send(v) : v;
  endfunction endclass
class corrupt extends hook;
  virtual function int on_send(int v); return v ^ 1; endfunction endclass
module top; driver drv; corrupt c;
  initial begin drv = new; c = new; drv.cb = c;
    $display("sent=%0d", drv.send(4));
    if (drv.send(4) == 5) $display("PROBE o34 PASS");
    else $display("PROBE o34 FAIL"); $finish; end
endmodule
