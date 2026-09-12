class c; rand bit [7:0] v; endclass
module top; c o; int ok; initial begin o = new(); ok = o.randomize() with { v inside {[10:20]}; };
  if (ok==1 && o.v>=10 && o.v<=20) $display("PROBE k14 PASS"); else $display("PROBE k14 FAIL"); $finish; end endmodule
