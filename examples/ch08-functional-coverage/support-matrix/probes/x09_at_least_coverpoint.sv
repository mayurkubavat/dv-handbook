// option.at_least = 2 at the coverpoint: 0 is sampled twice and 1 once,
// so only bin 0 of four is covered; the standard gives 25.00 (x09)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v { option.at_least = 2; } endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); g.sample(); v = 1; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 25.0)) $display("PROBE x09 PASS");
    else $display("PROBE x09 FAIL");
    $finish;
  end
endmodule
