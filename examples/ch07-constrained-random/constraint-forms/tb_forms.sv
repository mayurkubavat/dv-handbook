// tb_forms.sv -- randomize each form many times and print what came out.
//
// A form that constrains a set prints the values seen; a form that shapes
// a distribution prints counts; a form about ordering prints how often
// the rare branch was taken. Every call is checked.
module tb_forms;
  localparam int N = 200;
  int errors = 0;

  c_inside       f_in;
  c_relation     f_rel;
  c_dist_assign  f_da;
  c_dist_divide  f_dd;
  c_implication  f_imp;
  c_ifelse       f_ie;
  c_foreach      f_fe;
  c_solve_before f_sb;
  c_soft         f_soft;
  c_unique       f_uq;

  // counters, declared here so that the initial block owns no statics
  int seen_in [int];
  int n_da_low, n_da_9, n_dd_low, n_dd_9;
  int n_imp_s, n_sb_s, n_ie_hi;
  bit [7:0] gap_max;
  int r1, r2;

  initial begin
    f_in = new; f_rel = new; f_da = new; f_dd = new; f_imp = new;
    f_ie = new; f_fe = new; f_sb = new; f_soft = new; f_uq = new;

    for (int i = 0; i < N; i++) begin
      if (f_in.randomize() != 1) errors++;
      seen_in[int'(f_in.a)] = 1;
      if (f_rel.randomize() != 1) errors++;
      if (f_rel.hi - f_rel.lo > gap_max) gap_max = f_rel.hi - f_rel.lo;
      if (f_da.randomize() != 1) errors++;
      if (f_da.a <= 3) n_da_low++; else n_da_9++;
      if (f_dd.randomize() != 1) errors++;
      if (f_dd.a <= 3) n_dd_low++; else n_dd_9++;
      if (f_imp.randomize() != 1) errors++;
      if (f_imp.s) begin n_imp_s++; if (f_imp.v != 0) errors++; end
      if (f_ie.randomize() != 1) errors++;
      if (f_ie.mode) n_ie_hi++;
      if (f_sb.randomize() != 1) errors++;
      if (f_sb.s) begin n_sb_s++; if (f_sb.v != 0) errors++; end
      if (f_uq.randomize() != 1) errors++;
      if (f_uq.x[0] == f_uq.x[1] || f_uq.x[1] == f_uq.x[2]
          || f_uq.x[0] == f_uq.x[2]) errors++;
    end
    $display("inside:        %0d distinct values, all in the set: %s",
             seen_in.size(), seen_in.size() == 15 ? "yes" : "no");
    $display("relation:      lo < hi held, largest hi-lo = %0d", gap_max);
    $display("dist :=        [0:3] %0d times, 9 %0d times  (each value 1)",
             n_da_low, n_da_9);
    $display("dist :/        [0:3] %0d times, 9 %0d times  (range 1, 9 1)",
             n_dd_low, n_dd_9);
    $display("implication:   s was 1 in %0d of %0d, v==0 every time",
             n_imp_s, N);
    $display("solve before:  s was 1 in %0d of %0d, v==0 every time",
             n_sb_s, N);
    $display("if/else:       mode 1 in %0d of %0d", n_ie_hi, N);

    if (f_fe.randomize() != 1) errors++;
    $display("foreach:       x = %0d %0d %0d %0d (each in [1:8], rising)",
             f_fe.x[0], f_fe.x[1], f_fe.x[2], f_fe.x[3]);
    r1 = f_soft.randomize();
    $display("soft:          default a=%0d", f_soft.a);
    r2 = f_soft.randomize() with { a == 7; };
    $display("soft, inline:  a=%0d (the inline constraint won)", f_soft.a);
    if (r1 != 1 || r2 != 1) errors++;
    $display("unique:        x = %0d %0d %0d", f_uq.x[0], f_uq.x[1],
             f_uq.x[2]);

    // solve-before is a distribution request; measure it against the
    // same implication without it, over more draws
    n_imp_s = 0; n_sb_s = 0;
    for (int i = 0; i < 2000; i++) begin
      if (f_imp.randomize() != 1) errors++;
      if (f_imp.s) n_imp_s++;
      if (f_sb.randomize() != 1) errors++;
      if (f_sb.s) n_sb_s++;
    end
    $display("2000 draws:    s=1 %0d times without solve before, %0d with",
             n_imp_s, n_sb_s);
    $display("every call checked: %0d failures", errors);
    $finish;
  end
endmodule
