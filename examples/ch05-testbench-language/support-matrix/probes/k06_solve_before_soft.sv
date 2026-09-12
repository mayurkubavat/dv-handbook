// A soft constraint and a solve-before ordering. A tool that ignores the
// constraints still returns 1 from randomize(), so the probe checks the
// value the soft constraint asked for rather than the return code.
class c; rand bit a; rand bit [3:0] b;
  constraint c1 { solve a before b; }
  constraint c2 { soft b == 3; } endclass
module top; c o; int ok; initial begin o = new(); ok = o.randomize();
  if (ok == 1 && o.b == 3) $display("PROBE k06 PASS");
  else $display("PROBE k06 FAIL"); $finish; end endmodule
