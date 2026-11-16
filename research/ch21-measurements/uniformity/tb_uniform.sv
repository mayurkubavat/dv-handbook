// tb_uniform.sv -- draw from the Chapter 7 constraint shapes many times
// and print every value, so that Python can test the draws against the
// distribution each constraint asks for. Classes are rewritten from
// examples/ch07-constrained-random/{distribution,constraint-forms} and
// examples/ch07-constrained-random/packet-stream/rand_packet.sv.
// Output: one line per draw, "D <name> <value>". +only_ranged draws
// the first class alone, for a longer run of it.
class ranged;                         // uniform over 0..32767 asked
  rand bit [15:0] v;
  constraint c { v < 16'h8000; }
endclass

class w_values;                       // := every value carries its weight
  rand bit [7:0] v;
  constraint c { v dist { [0:9] := 1, [10:99] := 1, [100:255] := 2 }; }
endclass

class w_ranges;                       // :/ each range shares its weight
  rand bit [7:0] v;
  constraint c { v dist { [0:9] :/ 1, [10:99] :/ 1, [100:255] :/ 2 }; }
endclass

class kind_mix;                       // the packet's kind mix 6:3:1
  rand bit [1:0] kind;
  constraint contract { kind != 2'd3; }
  constraint mix      { kind dist { 0 :/ 6, 1 :/ 3, 2 :/ 1 }; }
endclass

class impl;                           // 257 solutions; s=1 has one
  rand bit       s;
  rand bit [7:0] v;
  constraint c { s -> v == 0; }
endclass

class impl_sb;                        // the same, s solved first
  rand bit       s;
  rand bit [7:0] v;
  constraint c { s -> v == 0; solve s before v; }
endclass

module tb_uniform;
  int n, errors;
  bit only;
  ranged r; w_values wv; w_ranges wr; kind_mix km; impl im; impl_sb is;
  initial begin
    if (!$value$plusargs("n=%d", n)) n = 1000;
    only = $test$plusargs("only_ranged");
    r = new; wv = new; wr = new; km = new; im = new; is = new;
    for (int i = 0; i < n; i++) begin
      if (r.randomize() != 1) errors++;
      $display("D ranged %0d", r.v);
      if (only) continue;
      if (wv.randomize() != 1) errors++;
      $display("D w_values %0d", wv.v);
      if (wr.randomize() != 1) errors++;
      $display("D w_ranges %0d", wr.v);
      if (km.randomize() != 1) errors++;
      $display("D kind %0d", km.kind);
      if (im.randomize() != 1) errors++;
      $display("D impl %0d", im.s ? 256 : int'(im.v));
      if (is.randomize() != 1) errors++;
      $display("D impl_sb %0d", is.s ? 256 : int'(is.v));
    end
    $display("ERRORS %0d", errors);
    $finish;
  end
endmodule
