// tb_lifetime.sv -- automatic and static, read off the declaration.
//
// A task in a module is static: one copy of its variables, shared by every
// call, so two concurrent calls can corrupt each other. Declared
// `automatic`, each call gets its own. Whether the static version *does*
// corrupt depends on how the simulator interleaves the two callers, which
// is why this runs under both: one shows the corruption and one does not.
module tb_lifetime;
  // static by default in a module: `n` is one variable for every caller
  task count_static(input int start, output int last);
    int n;
    n = start;
    #5 n = n + 1;         // a second call can overwrite n meanwhile
    last = n;
  endtask
  task automatic count_auto(input int start, output int last);
    int n;
    n = start;
    #5 n = n + 1;
    last = n;
  endtask
  int s1, s2, a1, a2;
  initial begin
    fork
      count_static(10, s1);
      count_static(20, s2);
    join
    fork
      count_auto(10, a1);
      count_auto(20, a2);
    join
    $display("static task, two callers: %0d %0d  (expected 11 21)", s1, s2);
    $display("automatic task, two callers: %0d %0d  (expected 11 21)",
             a1, a2);
    $finish;
  end
endmodule
