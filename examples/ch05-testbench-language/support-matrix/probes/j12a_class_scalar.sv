class packet; int id; int len;
  function new(int i = 0); id = i; len = 0; endfunction
  function void grow(); len++; endfunction
  function packet copy(); packet p = new(id); p.len = len; return p; endfunction
endclass
module top; packet a, b, c;
  initial begin a = new(1); a.grow(); b = a; c = a.copy(); b.id = 2; c.grow();
    $display("a.id=%0d c.id=%0d a.len=%0d c.len=%0d", a.id, c.id, a.len, c.len);
    if (a.id==2 && c.id==1 && a.len==1 && c.len==2 && b!=null) $display("PROBE j12a PASS"); else $display("PROBE j12a FAIL"); $finish; end
endmodule
