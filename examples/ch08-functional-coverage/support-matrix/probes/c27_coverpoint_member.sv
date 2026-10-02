// get_inst_coverage() on a coverpoint through the instance,
// g.cp.get_inst_coverage(): the 2-bit coverpoint sees 0 and 1; the
// standard gives 50.00 (c27)
module top;
  bit [1:0] v;
  covergroup cg; cp: coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample();
    $display("cp=%0.2f", g.cp.get_inst_coverage());
    if (near(g.cp.get_inst_coverage(), 50.0)) $display("PROBE c27 PASS");
    else $display("PROBE c27 FAIL");
    $finish;
  end
endmodule
