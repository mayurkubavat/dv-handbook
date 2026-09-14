// tb_seeds.sv -- what replays a random sequence and what does not.
//
// Three generators are asked for the same values twice. An object's
// generator, reseeded with srandom(), replays. A thread's generator,
// reseeded through process::self().srandom(), replays. The thread's
// generator reseeded through $urandom(seed) is measured, not assumed:
// the values after the two calls are printed side by side.
class txn;
  rand bit [31:0] a;
endclass

module tb_seeds;
  txn p, q;
  bit [31:0] s1[3], s2[3], t1[3], t2[3];
  bit [31:0] dummy, first;
  bit obj_same, thr_same, sys_same;

  initial begin
    first = $urandom();                  // before any reseeding below
    // 1. two objects, the same seed, the same randomize() sequence
    p = new; q = new;
    p.srandom(7); q.srandom(7);
    obj_same = 1;
    for (int i = 0; i < 3; i++) begin
      if (p.randomize() != 1 || q.randomize() != 1) $fatal(1, "no solver");
      if (p.a != q.a) obj_same = 0;
    end
    $display("object srandom(7) twice: %0d %0d ... %s", p.a, q.a,
             obj_same ? "same sequence" : "different");

    // 2. two threads, each reseeding its own generator
    fork
      begin process::self().srandom(11);
        for (int i = 0; i < 3; i++) t1[i] = $urandom(); end
      begin process::self().srandom(11);
        for (int i = 0; i < 3; i++) t2[i] = $urandom(); end
    join
    thr_same = (t1[0] == t2[0] && t1[1] == t2[1] && t1[2] == t2[2]);
    $display("thread srandom(11) twice: %0d %0d ... %s", t1[0], t2[0],
             thr_same ? "same sequence" : "different");

    // 3. $urandom(seed) twice in one thread, values after each
    dummy = $urandom(42);
    for (int i = 0; i < 3; i++) s1[i] = $urandom();
    dummy = $urandom(42);
    for (int i = 0; i < 3; i++) s2[i] = $urandom();
    sys_same = (s1[0] == s2[0] && s1[1] == s2[1] && s1[2] == s2[2]);
    $display("$urandom(42) twice:      %0d %0d ... %s", s1[0], s2[0],
             sys_same ? "same sequence" : "different");
    $display("first draw of this run:  %0d", first);
    $finish;
  end
endmodule
