// option.at_least = 2 at the covergroup level: 0 is sampled twice and 1
// once, so only bin 0 of four is covered; the standard gives 25.00 (a
// tool that drops the option prints 50.00) (c24)
module top;
  bit [1:0] v;
  covergroup cg; option.at_least = 2; coverpoint v; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); g.sample(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 25.0)) $display("PROBE c24 PASS");
    else $display("PROBE c24 FAIL");
    $finish;
  end
endmodule
