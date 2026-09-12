class c; rand bit a; rand bit [3:0] b;
  constraint c1 { solve a before b; }
  constraint c2 { soft b == 3; } endclass
module top; c o; int ok; initial begin o = new(); ok = o.randomize();
  if (ok==1) $display("PROBE k06 PASS"); else $display("PROBE k06 FAIL"); $finish; end endmodule
