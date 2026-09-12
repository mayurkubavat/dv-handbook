// tb_aggregates.sv -- one value, four containers.
//
// The choice is made by two questions: what is the index, and is the size
// known when the code is written? A fixed array answers both up front; a
// dynamic array defers the size; a queue is a dynamic array that grows and
// shrinks at both ends; an associative array is indexed by a key of any
// type and holds only the entries that were written.
module tb_aggregates;
  logic [7:0] fixed [4];            // size 4, forever
  logic [7:0] dyn [];               // size decided at run time
  logic [7:0] q [$];                // a queue: push, pop, insert, delete
  logic [7:0] byaddr [int];         // an associative array keyed by int
  logic [7:0] v;
  int i;
  initial begin
    foreach (fixed[k]) fixed[k] = 8'(8'h10 * k);
    dyn = new[3];
    foreach (dyn[k]) dyn[k] = 8'(8'hA0 + k);
    dyn = new[5] (dyn);             // grow, keeping the old contents
    $display("fixed: %0d entries; dyn: %0d entries after new[5](dyn)",
             $size(fixed), dyn.size());
    q.push_back(8'h01); q.push_back(8'h02); q.push_front(8'h00);
    q.insert(2, 8'hFF);
    $display("queue after push/push/push_front/insert: %p size=%0d",
             q, q.size());
    v = q.pop_front();
    $display("pop_front -> %02h; q[$] (last) = %02h", v, q[$]);
    byaddr[32'h1000] = 8'h55; byaddr[32'h2000] = 8'h66; byaddr[-1] = 8'h77;
    $display("assoc: %0d entries, exists(1000h)=%0d exists(1234h)=%0d",
             byaddr.num(), byaddr.exists(32'h1000), byaddr.exists(32'h1234));
    if (byaddr.first(i) != 0)
      do $display("  byaddr[%0h] = %02h", i, byaddr[i]);
      while (byaddr.next(i) != 0);
    byaddr.delete(32'h2000);
    $display("after delete(2000h): %0d entries", byaddr.num());
    $finish;
  end
endmodule
