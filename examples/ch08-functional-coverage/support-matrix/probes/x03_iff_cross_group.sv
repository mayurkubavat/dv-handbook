// iff on a cross, judged through the group: cross ca, cb iff (en); (0,0)
// is sampled with en high and (1,1) with en low, so ca and cb are at
// 100 and the cross at 25; the average is 75.00 (a tool that divides
// 5 bins hit by 8 prints 62.50) (x03)
module top;
  bit en, a, b;
  covergroup cg; ca: coverpoint a; cb: coverpoint b;
    ab: cross ca, cb iff (en);
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    en = 1; a = 0; b = 0; g.sample(); en = 0; a = 1; b = 1; g.sample();
    $display("group=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 75.0)) $display("PROBE x03 PASS");
    else $display("PROBE x03 FAIL");
    $finish;
  end
endmodule
