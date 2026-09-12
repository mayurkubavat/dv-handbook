// A covergroup inside a class, sampled four times over a two-bit point.
// The probe checks that the four samples were counted, not only that the
// construct was accepted.
class mon; bit [1:0] op;
  covergroup cg; coverpoint op; endgroup
  function new(); cg = new(); endfunction
  function void see(bit [1:0] o); op = o; cg.sample(); endfunction endclass
module top; mon m; initial begin m = new(); m.see(0); m.see(1); m.see(2); m.see(3);
  if (m.cg.get_inst_coverage() == 100.0) $display("PROBE k08 PASS");
  else $display("PROBE k08 FAIL"); $finish; end endmodule
