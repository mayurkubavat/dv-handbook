class mon; bit [1:0] op;
  covergroup cg; coverpoint op; endgroup
  function new(); cg = new(); endfunction
  function void see(bit [1:0] o); op = o; cg.sample(); endfunction endclass
module top; mon m; initial begin m = new(); m.see(0); m.see(1); m.see(2); m.see(3);
  $display("PROBE k08 PASS"); $finish; end endmodule
