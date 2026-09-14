// rand_packet.sv -- the previous chapter's environment, fed by constraints.
//
// Nothing in env.sv changes. A derived packet draws its own fields, a
// maker that checks every randomize() replaces the fixed sequence, and a
// callback counts what was generated, because a mix that was asked for
// is a mix to be measured.
class rand_packet extends packet;
  rand bit [1:0] kind;
  rand bit [5:0] seq;
  constraint contract { kind != 2'd3; }             // legal(), as a rule
  constraint mix      { kind dist { 0 :/ 6, 1 :/ 3, 2 :/ 1 }; }
  constraint nonzero  { seq inside {[1:63]}; }
  function new();
    super.new(2'd0, 6'd0);
  endfunction
  function void post_randomize();                   // copy into the word
    word.kind = kind;
    word.seq  = seq;
  endfunction
endclass

class random_maker extends packet_maker;            // the factory hole
  virtual function packet create(int i);
    rand_packet p = new;
    if (p.randomize() != 1)
      $fatal(1, "packet %0d: randomize() returned 0", i);
    return p;
  endfunction
endclass

class histogram_cb extends packet_cb;               // the callback hole
  int by_kind[4];
  virtual function void on_send(packet p);
    by_kind[int'(p.word.kind)]++;
  endfunction
endclass
