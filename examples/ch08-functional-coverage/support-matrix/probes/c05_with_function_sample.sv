// covergroup ... with function sample(args): the argument is the
// coverpoint; sample(0) and sample(3) on 2 bits give 50.00 (c05)
module top;
  covergroup cg with function sample(bit [1:0] x); coverpoint x; endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    g.sample(0); g.sample(3);
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c05 PASS");
    else $display("PROBE c05 FAIL");
    $finish;
  end
endmodule
