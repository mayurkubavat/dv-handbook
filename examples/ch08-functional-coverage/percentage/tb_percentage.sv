// tb_percentage.sv -- one group, two coverpoints of four and two bins;
// the tool's get_inst_coverage() beside the standard's rule, both
// computed from the same hit counts the testbench tracks itself.
module tb_percentage;
  localparam int N_OP = 4, N_DIR = 2;    // bins per coverpoint
  bit [1:0] op;                          // four values, four bins
  bit       dir;                         // two values, two bins

  covergroup cg;
    cp_op:  coverpoint op  { bins v[] = {[0:N_OP-1]}; }
    cp_dir: coverpoint dir { bins v[] = {[0:N_DIR-1]}; }
  endgroup
  cg g;

  bit  seen_op[N_OP], seen_dir[N_DIR];   // which values were sampled
  int  hit_op, hit_dir;
  real tool, ratio, average;

  task drive(input bit [1:0] o, input bit d);
    op = o; dir = d; g.sample();
    seen_op[o] = 1; seen_dir[d] = 1;
  endtask

  initial begin
    g = new;
    drive(2'd2, 1'b0);
    drive(2'd2, 1'b1);                   // op hits one bin of four,
    drive(2'd2, 1'b1);                   // dir hits both of its two
    foreach (seen_op[i])  if (seen_op[i])  hit_op++;
    foreach (seen_dir[i]) if (seen_dir[i]) hit_dir++;
    tool    = g.get_inst_coverage();
    ratio   = 100.0 * (hit_op + hit_dir) / (N_OP + N_DIR);
    average = (100.0 * hit_op / N_OP + 100.0 * hit_dir / N_DIR) / 2.0;
    $display("cp_op : %0d of %0d bins hit", hit_op, N_OP);
    $display("cp_dir: %0d of %0d bins hit", hit_dir, N_DIR);
    $display("get_inst_coverage()   : %0.2f", tool);
    $display("bins hit over defined : %0.2f  (%0d/%0d; the tool's rule)",
             ratio, hit_op + hit_dir, N_OP + N_DIR);
    $display("average of the items  : %0.2f  (IEEE 1800 19.11, weight 1)",
             average);
    if (tool - ratio > 0.005 || ratio - tool > 0.005)
      $fatal(1, "the tool no longer follows the bins ratio; re-measure");
    $display("verdict: tool %0.2f (%0d of %0d bins); standard's average %0.2f",
             tool, hit_op + hit_dir, N_OP + N_DIR, average);
    $finish;
  end
endmodule
