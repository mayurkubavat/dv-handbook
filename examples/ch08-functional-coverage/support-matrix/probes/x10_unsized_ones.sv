// bin value '1 on an 8-bit coverpoint: bins ones = {'1} must match 8'hff
// beside bins zero = {0}; one sample of 8'hff hits ones; the standard
// gives 50.00 (a tool that widens '1 to 8'h01 prints 0.00) (x10)
module top;
  bit [7:0] v;
  covergroup cg; coverpoint v { bins ones = {'1}; bins zero = {0}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 8'hff; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE x10 PASS");
    else $display("PROBE x10 FAIL");
    $finish;
  end
endmodule
