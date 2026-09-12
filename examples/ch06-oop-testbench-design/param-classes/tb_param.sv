// tb_param.sv -- a parameterized class is a family of distinct types.
//
// `box #(int)` and `box #(string)` are not two views of one class; each
// specialization is its own type with its own static members and its own
// place in the hierarchy. So the two counters below are two counters, and
// a handle of one specialization cannot be cast to the other.
class box #(type T = int);
  static int made = 0;
  T contents;
  function new(T c); contents = c; made++; endfunction
endclass

typedef box #(int)    int_box;
typedef box #(string) str_box;

module tb_param;
  int_box ib1, ib2, ib3;
  str_box sb1;
  initial begin
    ib1 = new(1); ib2 = new(2); ib3 = new(3);
    sb1 = new("one");
    $display("box#(int) made %0d, box#(string) made %0d",
             int_box::made, str_box::made);
    $display("int_box::made == box#(int)::made: %0d",
             int_box::made == box#(int)::made);
    $finish;
  end
endmodule
