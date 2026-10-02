// tb_cross.sv -- a 4-bit variable crossed with a 10-bin coverpoint is
// 160 cross bins (IEEE 1800 19.6). The second group keeps only the
// tuples that matter by binning the point first; run_cross.sh reads
// both crosses' bins from the coverage database.
module tb_cross;
  bit [3:0] a;
  bit [7:0] b;

  covergroup cg_full;
    ca: coverpoint a;                    // auto bins: 16
    cb: coverpoint b { bins lo[] = {[0:9]}; }    // 10 named bins
    ab: cross ca, cb;                    // 16 x 10 = 160 cross bins
  endgroup

  covergroup cg_small;
    ca: coverpoint a { bins lo[] = {[0:3]}; }    // only the values used
    cb: coverpoint b { bins lo[] = {[0:9]}; }
    ab: cross ca, cb;                    // 4 x 10 = 40 cross bins
  endgroup
  cg_full  g_full;
  cg_small g_small;

  initial begin
    g_full = new; g_small = new;
    for (int i = 0; i < 4; i++)          // a fixed 12-sample stimulus
      for (int j = 0; j < 3; j++) begin
        a = 4'(i); b = 8'(j);
        g_full.sample(); g_small.sample();
      end
    $display("cg_full  get_inst_coverage(): %0.2f",
             g_full.get_inst_coverage());
    $display("cg_small get_inst_coverage(): %0.2f",
             g_small.get_inst_coverage());
    $finish;
  end
endmodule
