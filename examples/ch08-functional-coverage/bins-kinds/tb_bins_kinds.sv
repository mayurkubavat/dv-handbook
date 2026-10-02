// tb_bins_kinds.sv -- every kind of bin on one 8-bit value: array,
// value, range, range to $, wildcard, ignore, default and transition.
// A fixed sequence hits every bin the standard counts; the group's own
// percentage is printed beside the per-bin counts that run_bins.sh
// reads back from the coverage database.
module tb_bins_kinds;
  bit [7:0] v;

  covergroup g;
    cp_val: coverpoint v {
      bins b[]        = {[0:3]};         // array: b[0] .. b[3]
      bins four       = {4};             // one value
      bins low        = {[5:63]};        // a range
      wildcard bins w = {8'b01??_????};  // 64 .. 127
      bins high       = {[192:$]};       // 192 .. the maximum
      ignore_bins ig  = {2};             // reserved: not a bin at all
      bins rest       = default;         // 128 .. 191 land here
    }
    // The transitions have a coverpoint of their own: on 5.052 a
    // transition bin beside a default bin is an internal compiler error.
    cp_seq: coverpoint v {
      bins t01  = (0 => 1);              // a transition
      bins t013 = (0 => 1 => 3);         // a longer one
    }
  endgroup

  g gi;
  bit [7:0] seq[8] = '{0, 1, 3, 4, 10, 100, 200, 150};

  initial begin
    gi = new;
    $write("sequence sampled    :");
    foreach (seq[i]) begin
      v = seq[i]; gi.sample(); $write(" %0d", v);
    end
    $display("");
    $display("get_inst_coverage() : %0.2f", gi.get_inst_coverage());
    $display("by IEEE 1800        : 9 bins after ignore_bins, 9 hit, 100.00");
    $finish;
  end
endmodule
