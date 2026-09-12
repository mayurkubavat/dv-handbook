// tests.sv -- three tests, each filling one hole in the environment.
//
// None of them edits env.sv. The factory test substitutes a derived
// packet with a stricter contract; the override test changes what the
// driver does before each send; the callback test attaches a check the
// driver knows nothing about.

// --- test 1: the factory hole ------------------------------------------
class even_packet extends packet;         // a subtype: stricter, still legal
  function new(logic [1:0] kind, logic [5:0] seq);
    super.new(kind, {seq[5:1], 1'b0});    // every sequence number even
  endfunction
  virtual function bit legal();
    return super.legal() && !word.seq[0];
  endfunction
  virtual function string describe();
    return {"even ", super.describe()};
  endfunction
endclass
class even_maker extends packet_maker;
  virtual function packet create(int i);
    even_packet p = new(2'(i % 3), i[5:0]);
    return p;
  endfunction
endclass

// --- test 2: the virtual-step hole --------------------------------------
class inverting_driver extends driver;
  virtual task before_send(packet p);
    p.word.kind = 2'(p.word.kind + 1) % 3;  // change one step, keep the loop
  endtask
endclass

// --- test 3: the callback hole ------------------------------------------
class counting_cb extends packet_cb;
  int by_kind [4];
  virtual function void on_send(packet p);
    by_kind[p.word.kind]++;
  endfunction
endclass
