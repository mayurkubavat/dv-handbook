class txn; rand bit [7:0] addr; rand bit [3:0] len; endclass
module top; txn t; int ok, i, changed; bit [7:0] first;
  initial begin t = new(); changed = 0; ok = t.randomize(); first = t.addr;
    for (i = 0; i < 20; i++) begin ok = t.randomize(); if (t.addr != first) changed++; end
    $display("ok=%0d changed=%0d", ok, changed);
    if (ok==1 && changed>0) $display("PROBE i18a PASS"); else $display("PROBE i18a FAIL"); $finish; end
endmodule
