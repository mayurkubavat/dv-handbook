// range bins with $: bins lo = {[0:3]} and bins hi = {[12:$]} on 4 bits;
// one sample of 15 hits hi only; the standard gives 50.00 (c07)
module top;
  bit [3:0] v;
  covergroup cg; coverpoint v { bins lo = {[0:3]}; bins hi = {[12:$]}; }
  endgroup
  cg g;
  function automatic bit near(real a, real b);
    return (a - b) < 0.01 && (b - a) < 0.01;
  endfunction
  initial begin
    g = new;
    v = 15; g.sample();
    $display("cov=%0.2f", g.get_inst_coverage());
    if (near(g.get_inst_coverage(), 50.0)) $display("PROBE c07 PASS");
    else $display("PROBE c07 FAIL");
    $finish;
  end
endmodule
