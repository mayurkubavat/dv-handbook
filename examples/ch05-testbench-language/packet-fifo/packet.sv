// packet.sv -- one transaction: a packed struct inside a class.
//
// The struct is the wire format: what the FIFO stores, bit for bit. The
// class is the testbench's object: it has an identity, a construction
// time, and a comparison method. The scoreboard keeps handles to packets
// in a queue, in the order they were sent, and pops them as they arrive.
typedef struct packed {
  logic [1:0] kind;
  logic [5:0] seq;
} word_t;                          // eight bits: the FIFO's WIDTH

class packet;
  static int made = 0;
  int    id;
  word_t word;
  function new(logic [1:0] kind, logic [5:0] seq);
    word.kind = kind; word.seq = seq;
    id = made++;
  endfunction
  function bit same(word_t w);
    return w == word;
  endfunction
  function string str();
    return $sformatf("#%0d kind=%0d seq=%0d", id, word.kind, word.seq);
  endfunction
endclass
