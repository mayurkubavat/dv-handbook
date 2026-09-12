// tb_structs.sv -- a bus transaction as a packed struct, and the enum hole.
//
// A packed struct is a vector with named fields: the same bits can be read
// by name or as a whole, and a union of two packed layouts is an honest
// reinterpretation of one set of bits. An enum is a type with a closed set
// of names -- closed for `$cast` and for `.next()`, which refuse a value
// outside the set, and open for a static cast, which forces one in.
typedef struct packed {
  logic [3:0]  tag;
  logic [11:0] addr;
  logic [15:0] data;
} bus_txn_t;                      // 32 bits, tag in the top four

typedef union packed {
  bus_txn_t    fields;
  logic [31:0] raw;
} bus_word_t;

typedef enum logic [1:0] {IDLE = 2'd0, BUSY = 2'd1, DONE = 2'd2} state_t;

module tb_structs;
  bus_word_t w;
  state_t    s;
  int        ok;
  initial begin
    w.raw = 32'hA_123_BEEF;
    $display("raw=%08h tag=%h addr=%03h data=%04h",
             w.raw, w.fields.tag, w.fields.addr, w.fields.data);
    w.fields.tag = 4'hF;
    $display("after fields.tag = F: raw=%08h", w.raw);
    s = IDLE;
    $display("%s.next() = %s, num()=%0d", s.name(), s.next().name(),
             s.num());
    ok = $cast(s, 2'd3);          // 3 is not in the set: refused
    $display("$cast(s, 3) returned %0d; s is still %s", ok, s.name());
    s = state_t'(2'd3);           // a static cast forces it in
    $display("state_t'(3): s=%0d name=\"%s\"", s, s.name());
    $finish;
  end
endmodule
