// tb_per_instance.sv -- one covergroup type, two named instances that
// each see one half of a two-bin coverpoint: the instance numbers, and
// the type number as Verilator 5.052 reports it.
module tb_per_instance;
  covergroup cg (string inst) with function sample(bit is_full);
    option.per_instance = 1;             // keep and report each instance
    option.name         = inst;          // instead of a generated name
    cp: coverpoint is_full { bins empty = {0}; bins full = {1}; }
  endgroup
  cg port0, port1;
  real inst0, inst1, type_cov;

  initial begin
    port0 = new("port0");
    port1 = new("port1");
    port0.sample(1'b0);                  // port0 only ever sees empty
    port1.sample(1'b1);                  // port1 only ever sees full
    inst0    = port0.get_inst_coverage();
    inst1    = port1.get_inst_coverage();
    type_cov = port0.get_coverage();     // the type: both instances
    $display("port0 get_inst_coverage(): %0.2f", inst0);
    $display("port1 get_inst_coverage(): %0.2f", inst1);
    $display("cg    get_coverage()     : %0.2f  (measured on 5.052)",
             type_cov);
    $display("IEEE 1800 19.11.3: average of the instances, %0.2f;",
             (inst0 + inst1) / 2.0);
    $display("  or their union, 100.00, with type_option.merge_instances");
    $display("verdict: instances %0.2f, %0.2f; type %0.2f, IEEE says 50 or 100",
             inst0, inst1, type_cov);
    $finish;
  end
endmodule
