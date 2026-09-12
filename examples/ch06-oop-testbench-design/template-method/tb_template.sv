// tb_template.sv -- a base algorithm with a virtual step.
//
// `run` is written once, in the base class, and never overridden. It
// calls `step`, which is virtual, so a derived class changes what one step
// does without touching the algorithm around it. This is the shape every
// verification driver has: the base owns the loop and the reset handling,
// the derived class owns what one transaction looks like on the wires.
// On a simulator that ignores `virtual`, the base's `step` runs even
// through the derived handle, because the call is made from base code.
class driver;
  int total;
  task run(int n);                         // the algorithm: fixed
    total = 0;
    for (int i = 0; i < n; i++) step(i);
  endtask
  virtual task step(int i);                // the hole: overridable
    total += i;
  endtask
endclass
class doubling_driver extends driver;
  virtual task step(int i);
    total += 2 * i;
  endtask
endclass

module tb_template;
  doubling_driver d;
  initial begin
    d = new;
    d.run(4);
    $display("total after run(4): %0d  (doubling: 12; base: 6)", d.total);
    $finish;
  end
endmodule
