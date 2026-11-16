// tb_draws.sv -- draws from Chapter 7's own constraint classes, printed
// one per line ("D <class> <value>") so that a Python script can test
// each histogram against the law its constraint asks for. The classes
// come from Chapter 7's files, compiled by path beside this one:
// forms.sv (the dist, implication and solve...before forms) and
// rand_packet.sv (the packet kind mix). The one class defined here is
// the 16-bit range constraint of Chapter 7's distribution example,
// which lives inside that example's module and cannot be compiled
// alone. +n sets the draws per class; +cls=<name> draws from one class
// only, so that a runner can draw the six in parallel processes.
class range16;                        // the distribution example's range
  rand bit [15:0] v;
  constraint c { v < 16'h8000; }
endclass

module tb_draws;
  int n, errors;
  string cls;
  range16        r;
  c_dist_assign  da;
  c_dist_divide  dd;
  c_implication  im;
  c_solve_before sb;
  rand_packet    pk;

  function automatic bit want(string name);
    return cls == "all" || cls == name;
  endfunction

  initial begin
    if (!$value$plusargs("n=%d", n)) n = 2000;
    if (!$value$plusargs("cls=%s", cls)) cls = "all";
    r = new; da = new; dd = new; im = new; sb = new; pk = new;
    for (int i = 0; i < n; i++) begin
      if (want("range16")) begin
        if (r.randomize() != 1) errors++;
        $display("D range16 %0d", r.v);
      end
      if (want("dist_assign")) begin
        if (da.randomize() != 1) errors++;
        $display("D dist_assign %0d", da.a);
      end
      if (want("dist_divide")) begin
        if (dd.randomize() != 1) errors++;
        $display("D dist_divide %0d", dd.a);
      end
      if (want("implication")) begin
        if (im.randomize() != 1) errors++;
        $display("D implication %0d", im.s ? 256 : int'(im.v));
      end
      if (want("solve_before")) begin
        if (sb.randomize() != 1) errors++;
        $display("D solve_before %0d", sb.s ? 256 : int'(sb.v));
      end
      if (want("kind")) begin
        if (pk.randomize() != 1) errors++;
        $display("D kind %0d", pk.kind);
      end
    end
    $display("randomize() failures in %s: %0d", cls, errors);
    $finish;
  end
endmodule
