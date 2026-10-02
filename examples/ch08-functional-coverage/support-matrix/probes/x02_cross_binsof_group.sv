// cross with binsof ... intersect user bins, judged through the group:
// the cross has two user bins split by a; samples (0,0) and (0,1) give
// ca 50, cb 100 and cross 50, whose average is 66.67 (a tool that counts
// the auto cross instead prints 5/8, 62.50) (x02)
module top;
  bit a, b;
  covergroup cg; ca: coverpoint a; cb: coverpoint b;
    ab: cross ca, cb {
      bins a0 = binsof(ca) intersect {0};
      bins a1 = binsof(ca) intersect {1}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    a = 0; b = 0; g.sample(); a = 0; b = 1; g.sample();
    $display("group=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 66.67)) $display("PROBE x02 PASS");
    else $display("PROBE x02 FAIL");
    $finish;
  end
endmodule
