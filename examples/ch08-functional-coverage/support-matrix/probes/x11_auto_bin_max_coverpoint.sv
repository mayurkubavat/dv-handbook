// option.auto_bin_max = 2 at the coverpoint: a 4-bit coverpoint gets two
// bins, [0:7] and [8:15]; one sample of 3 hits one; the standard gives
// 50.00 (x11)
module top;
  bit [3:0] v;
  covergroup cg; coverpoint v { option.auto_bin_max = 2; } endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 3; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE x11 PASS");
    else $display("PROBE x11 FAIL");
    $finish;
  end
endmodule
