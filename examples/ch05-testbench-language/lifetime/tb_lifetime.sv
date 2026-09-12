// tb_lifetime.sv -- automatic and static, read off the declaration.
//
// A task in a module is static: one copy of its variables, shared by every
// call, so two concurrent calls corrupt each other. Declared `automatic`,
// each call gets its own. A class method is automatic by default, which is
// why `ref` arguments are legal there and not on a static task.
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
  // `ref` needs an automatic lifetime: the argument is a reference into the
  // caller's variable, and a static task has nowhere safe to keep it.
  task automatic bump(ref int x);
    x = x + 100;
  endtask

  int s1, s2, a1, a2, v = 1;
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
    bump(v);
    $display("after bump(ref v): v=%0d", v);
    $finish;
  end
endmodule
