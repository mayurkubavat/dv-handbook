// env.sv -- one environment, written once. Every class in it has a hole
// a test can fill without editing this file.
//
//   packet        the transaction; `legal` is the contract a derived class
//                 must keep -- kind 3 is reserved and never legal -- and
//                 `describe` is virtual so a derived packet prints itself
//   packet_maker  the factory: `create(i)` returns a base handle, and a
//                 test substitutes a maker that returns a derived packet
//   packet_cb     the callback: a hook object the driver calls before each
//                 send, for checks the test owns and the driver does not
//   driver        the template method: `run` is the algorithm; `before_send`
//                 is the virtual step a test overrides
//   scoreboard    a queue of expected packets and a comparison
typedef struct packed {
  logic [1:0] kind;
  logic [5:0] seq;
} word_t;

class packet;
  word_t word;
  function new(logic [1:0] kind, logic [5:0] seq);
    word.kind = kind; word.seq = seq;
  endfunction
  virtual function bit legal();          // the substitution contract
    return word.kind != 2'd3;
  endfunction
  virtual function string describe();
    return $sformatf("kind=%0d seq=%0d", word.kind, word.seq);
  endfunction
endclass

class packet_maker;                       // the factory
  virtual function packet create(int i);
    packet p = new(2'(i % 3), i[5:0]);   // kinds 0..2 only: never 3
    return p;
  endfunction
endclass

class packet_cb;                          // the callback hook
  virtual function void on_send(packet p); endfunction
endclass

class driver;
  virtual fifo_if vif;
  packet_maker maker;
  packet_cb    cb;
  packet       sent [$];
  task run(int n);                        // the template method: fixed
    packet p;
    for (int i = 0; i < n; i++) begin
      p = maker.create(i);
      before_send(p);
      if (cb != null) cb.on_send(p);
      sent.push_back(p);
      @(vif.cb);
      while (vif.cb.full) @(vif.cb);
      vif.cb.wr_en   <= 1;
      vif.cb.wr_data <= p.word;
      @(vif.cb);
      vif.cb.wr_en   <= 0;
    end
  endtask
  virtual task before_send(packet p);     // the virtual step: overridable
  endtask
endclass

class scoreboard;
  virtual fifo_if vif;
  int errors = 0, seen = 0;
  task run(int n, ref packet sent [$]);
    packet p;
    word_t w;
    for (int i = 0; i < n; i++) begin
      @(vif.cb);
      while (vif.cb.empty) @(vif.cb);
      w = vif.cb.rd_data;
      vif.cb.rd_en <= 1;
      @(vif.cb);
      vif.cb.rd_en <= 0;
      while (sent.size() == 0) @(vif.cb);
      p = sent.pop_front();
      seen++;
      if (w != p.word || !p.legal()) begin
        errors++;
        $display("  MISMATCH got kind=%0d seq=%0d expected %s legal=%0d",
                 w.kind, w.seq, p.describe(), p.legal());
      end
    end
  endtask
endclass
