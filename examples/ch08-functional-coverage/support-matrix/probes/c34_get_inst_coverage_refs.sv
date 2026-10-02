// two-argument get_inst_coverage(ref covered, ref total): the 2-bit
// coverpoint sees 0 and 1, so the call must return 50.00 and write
// covered = 2 and total = 4 (c34)
module top;
  bit [1:0] v;
  covergroup cg; coverpoint v; endgroup
  cg g;
  int covered, total; real c;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; g.sample(); v = 1; g.sample();
    c = g.get_inst_coverage(covered, total);
    $display("cov=%0.2f covered=%0d total=%0d", c, covered, total);
    if (near(c, 50.0) && covered == 2 && total == 4)
      $display("PROBE c34 PASS");
    else $display("PROBE c34 FAIL");
    $finish;
  end
endmodule
