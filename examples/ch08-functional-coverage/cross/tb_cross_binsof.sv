// tb_cross_binsof.sv -- the standard's way to drop tuples from a cross:
// ignore_bins with binsof ... intersect (IEEE 1800 19.6.2). Verilator
// 5.052 warns COVERIGN, fatal under -Wall, and keeps the auto cross;
// run_cross.sh builds this file with -Wno-fatal to show both.
module tb_cross_binsof;
  bit [3:0] a;
  bit [7:0] b;

  covergroup cg;
    ca: coverpoint a;                    // 16 auto bins
    cb: coverpoint b { bins lo[] = {[0:9]}; }
    ab: cross ca, cb {
      ignore_bins high_a = binsof(ca) intersect {[4:15]};  // 120 tuples
    }                                    // 160 - 120 = 40 bins remain
  endgroup
  cg g;

  initial begin
    g = new;
    for (int i = 0; i < 4; i++)          // the same 12-sample stimulus
      for (int j = 0; j < 3; j++) begin
        a = 4'(i); b = 8'(j);
        g.sample();
      end
    $display("cg get_inst_coverage(): %0.2f", g.get_inst_coverage());
    $finish;
  end
endmodule
