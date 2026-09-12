class outer; class inner; int v = 3; endclass inner i; function new(); i = new(); endfunction endclass
module top; outer o; initial begin o = new(); if (o.i.v==3) $display("PROBE k03 PASS"); else $display("PROBE k03 FAIL"); $finish; end endmodule
