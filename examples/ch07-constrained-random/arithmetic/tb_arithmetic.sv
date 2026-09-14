// tb_arithmetic.sv -- three constraints that compile, solve, and mean
// something other than what they say, because a constraint is an integer
// expression before it is a rule.
//
//   chained    lo < x < hi parses as (lo < x) < hi: a 1-bit result
//              compared with hi, which is true whenever hi > 1
//   weight     [0:10] :/ 1/11 is integer division, so the weight is 0
//   wrap       a - b < 4 on unsigned operands wraps when b > a, so the
//              "within 4" the author meant excludes every b above a
//
// Each class is randomized many times beside its corrected form, and the
// counts say which one holds.
class chained_wrong;
  rand bit [7:0] x;
  // The lint sees this one (WIDTHEXPAND: a 1-bit result compared
  // with an 8-bit value); the waiver keeps it so the solver's answer shows.
  /* verilator lint_off WIDTHEXPAND */
  constraint c { 8'd10 < x < 8'd20; }
  /* verilator lint_on WIDTHEXPAND */
endclass
class chained_right;
  rand bit [7:0] x;
  constraint c { 8'd10 < x; x < 8'd20; }
endclass

class weight_wrong;
  rand bit [3:0] a;
  constraint c { a dist { [0:10] :/ 1/11, 15 := 1 }; }
endclass
class weight_right;
  rand bit [3:0] a;
  constraint c { a dist { [0:10] :/ 1, 15 := 1 }; }
endclass

class wrap_wrong;
  rand bit [7:0] a, b;
  constraint c { a - b < 8'd4; }
endclass
class wrap_right;
  rand bit [7:0] a, b;
  constraint c { int'(a) - int'(b) inside {[-3:3]}; }
endclass

module tb_arithmetic;
  localparam int N = 1000;
  chained_wrong cw; chained_right cr;
  weight_wrong  ww; weight_right  wr;
  wrap_wrong    pw; wrap_right    pr;
  int in_w, in_r, low_w, low_r, below_w, below_r, errors;

  initial begin
    cw = new; cr = new; ww = new; wr = new; pw = new; pr = new;
    for (int i = 0; i < N; i++) begin
      if (cw.randomize() != 1) errors++;
      if (cw.x > 10 && cw.x < 20) in_w++;
      if (cr.randomize() != 1) errors++;
      if (cr.x > 10 && cr.x < 20) in_r++;
      if (ww.randomize() != 1) errors++;
      if (ww.a <= 10) low_w++;
      if (wr.randomize() != 1) errors++;
      if (wr.a <= 10) low_r++;
      if (pw.randomize() != 1) errors++;
      if (pw.b > pw.a) below_w++;
      if (pr.randomize() != 1) errors++;
      if (pr.b > pr.a) below_r++;
    end
    $display("chained  10 < x < 20 : %4d of %0d inside (10,20)", in_w, N);
    $display("split    10 < x; x<20: %4d of %0d inside (10,20)", in_r, N);
    $display("weight   [0:10] :/ 1/11: %4d of %0d in [0:10]", low_w, N);
    $display("weight   [0:10] :/ 1   : %4d of %0d in [0:10]", low_r, N);
    $display("unsigned a - b < 4     : %4d of %0d with b > a", below_w, N);
    $display("signed   int'(a)-int'(b): %4d of %0d with b > a", below_r, N);
    $display("every call returned 1: %s", errors == 0 ? "yes" : "no");
    $finish;
  end
endmodule
