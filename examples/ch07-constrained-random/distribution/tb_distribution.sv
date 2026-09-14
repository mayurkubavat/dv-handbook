// tb_distribution.sv -- a constraint names a set; what the solver draws
// from it is measured, not assumed.
//
// Ten thousand draws of a 16-bit value under one range constraint, then
// how often each of the low bits came out set: near half for a uniform
// draw, far from it for a solver that returns the same corner of the set.
// Then the same value under two `dist` constraints, whose weights are a
// request the tool honors or does not.
class ranged;
  rand bit [15:0] v;
  constraint c { v < 16'h8000; }
endclass

class weighted_ranges;                // :/ : the range shares the weight
  rand bit [7:0] v;
  constraint c { v dist { [0:9] :/ 1, [10:99] :/ 1, [100:255] :/ 2 }; }
endclass

class weighted_values;                // := : every value gets the weight
  rand bit [7:0] v;
  constraint c { v dist { [0:9] := 1, [10:99] := 1, [100:255] := 2 }; }
endclass

module tb_distribution;
  localparam int N = 10000;
  ranged r; weighted_ranges wr; weighted_values wv;
  int set[8], errors;
  int r_lo, r_mid, r_hi, v_lo, v_mid, v_hi;

  initial begin
    r = new; wr = new; wv = new;
    for (int i = 0; i < N; i++) begin
      if (r.randomize() != 1) errors++;
      for (int b = 0; b < 8; b++) if (r.v[b]) set[b]++;
      if (wr.randomize() != 1) errors++;
      if (wr.v < 10) r_lo++; else if (wr.v < 100) r_mid++; else r_hi++;
      if (wv.randomize() != 1) errors++;
      if (wv.v < 10) v_lo++; else if (wv.v < 100) v_mid++; else v_hi++;
    end
    $display("v < 16'h8000, %0d draws: low bit set in", N);
    for (int b = 0; b < 8; b++)
      $display("  bit %0d: %2d%%", b, (set[b] * 100) / N);
    $display("dist :/  [0:9] %4d  [10:99] %4d  [100:255] %4d  (1:1:2 asked)",
             r_lo, r_mid, r_hi);
    $display("dist :=  [0:9] %4d  [10:99] %4d  [100:255] %4d  (10:90:312)",
             v_lo, v_mid, v_hi);
    $display("every call returned 1: %s", errors == 0 ? "yes" : "no");
    $finish;
  end
endmodule
