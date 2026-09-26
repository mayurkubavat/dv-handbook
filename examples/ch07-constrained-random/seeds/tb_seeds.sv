// tb_seeds.sv -- what replays a random sequence and what does not.
//
// Five measurements, in an order that matters. First, before anything
// else has touched a generator: $urandom(seed) called twice as a void
// statement, then called twice with its result assigned to a variable
// nothing reads. Then an object reseeded with srandom(), and two threads
// each reseeding their own generator. Last, $urandom(seed) again, after
// those thread reseeds have happened in the run.
class txn;
  rand bit [31:0] a;
endclass

module tb_seeds;
  txn p, q;
  bit [31:0] s1[3], s2[3], t1[3], t2[3], u1[3], u2[3], dummy, first;
  bit obj_same, thr_same;

  function automatic string same(bit [31:0] x[3], bit [31:0] y[3]);
    return (x[0] == y[0] && x[1] == y[1] && x[2] == y[2])
           ? "same sequence" : "different";
  endfunction

  initial begin
    first = $urandom();                  // before any reseeding below

    // 1. $urandom(seed) as a statement, twice, nothing else in between
    void'($urandom(42));
    for (int i = 0; i < 3; i++) s1[i] = $urandom();
    void'($urandom(42));
    for (int i = 0; i < 3; i++) s2[i] = $urandom();
    $display("void'($urandom(42)) twice:   %0d %0d ... %s", s1[0], s2[0],
             same(s1, s2));

    // 2. the same, with the result assigned to a variable never read
    dummy = $urandom(42);
    for (int i = 0; i < 3; i++) u1[i] = $urandom();
    dummy = $urandom(42);
    for (int i = 0; i < 3; i++) u2[i] = $urandom();
    $display("dummy = $urandom(42) twice:  %0d %0d ... %s", u1[0], u2[0],
             same(u1, u2));

    // 3. two objects, the same seed, the same randomize() sequence
    p = new; q = new;
    p.srandom(7); q.srandom(7);
    obj_same = 1;
    for (int i = 0; i < 3; i++) begin
      if (p.randomize() != 1 || q.randomize() != 1) $fatal(1, "no solver");
      if (p.a != q.a) obj_same = 0;
    end
    $display("object srandom(7) twice:     %0d %0d ... %s", p.a, q.a,
             obj_same ? "same sequence" : "different");

    // 4. two threads, each reseeding its own generator
    fork
      begin process::self().srandom(11);
        for (int i = 0; i < 3; i++) t1[i] = $urandom(); end
      begin process::self().srandom(11);
        for (int i = 0; i < 3; i++) t2[i] = $urandom(); end
    join
    $display("thread srandom(11) twice:    %0d %0d ... %s", t1[0], t2[0],
             same(t1, t2));

    // 5. measurement 1 again, now that threads have reseeded themselves
    void'($urandom(42));
    for (int i = 0; i < 3; i++) s1[i] = $urandom();
    void'($urandom(42));
    for (int i = 0; i < 3; i++) s2[i] = $urandom();
    $display("void'($urandom(42)) after 4: %0d %0d ... %s", s1[0], s2[0],
             same(s1, s2));
    $display("first draw of this run:      %0d", first);
    $finish;
  end
endmodule
