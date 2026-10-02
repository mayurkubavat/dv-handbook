// stop() / start(): 0 is sampled, then 1 while the group is stopped, then
// 0 again after start(); only bin 0 of four is hit; the standard gives
// 25.00 (a tool that drops stop() prints 50.00) (c28)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample();
    g.stop(); v = 1; g.sample();
    g.start(); v = 0; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 25.0)) $display("PROBE c28 PASS");
    else $display("PROBE c28 FAIL");
    $finish;
  end
endmodule
