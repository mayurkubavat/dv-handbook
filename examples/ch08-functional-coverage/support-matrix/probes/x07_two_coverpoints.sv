// two coverpoints of 4 and 2 bins, judged through the group: cp (2 bits)
// hits one bin of four and cw (1 bit) hits both of its two, so the
// items are at 25 and 100 and their average is 62.50 (a tool that
// divides 3 bins hit by 6 prints 50.00) (x07)
module top;
  bit [1:0] v; bit w;
  covergroup cg; cp: coverpoint v; cw: coverpoint w; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 0; w = 0; g.sample(); v = 0; w = 1; g.sample();
    $display("group=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 62.5)) $display("PROBE x07 PASS");
    else $display("PROBE x07 FAIL");
    $finish;
  end
endmodule
