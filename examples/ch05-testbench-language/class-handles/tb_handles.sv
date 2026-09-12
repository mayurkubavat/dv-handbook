// tb_handles.sv -- what a handle is, and what `=` does to one.
//
// A class variable names an object; it is not the object. Assigning one
// handle to another makes two names for one object, and a change through
// either is seen through both. A copy is something a method has to do.
// The static counter belongs to the class, not to any object, and every
// object sees the same one.
class packet;
  static int made = 0;      // one per class, not one per object
  int        id;
  logic [7:0] payload;
  function new(int id_, logic [7:0] payload_);
    id = id_; payload = payload_;
    made++;
  endfunction
  function packet copy();    // a copy is a new object with the same values
    copy = new(id, payload);
  endfunction
endclass

module tb_handles;
  packet a, b, c;
  initial begin
    $display("before new: a is %0s", a == null ? "null" : "an object");
    a = new(1, 8'h11);
    b = a;                   // alias: two handles, one object
    c = a.copy();            // copy: two objects
    b.payload = 8'h22;
    $display("after b.payload = 22h: a=%02h b=%02h c=%02h",
             a.payload, b.payload, c.payload);
    $display("objects made: %0d (a and c; b named a)", packet::made);
    a = null;
    $display("after a = null: b still %0s the object",
             b == null ? "lost" : "names");
    $finish;
  end
endmodule
