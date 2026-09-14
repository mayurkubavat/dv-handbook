// tb_nosolver.sv -- three constrained draws, printed with the return
// value of each call, so that a run without a solver shows what changes.
class txn;
  rand bit [7:0] len;
  constraint legal { len inside {[4:64]}; }
endclass
module tb_nosolver;
  txn t;
  int r;
  initial begin
    t = new;
    t.len = 8'd99;                       // a value the constraint forbids
    for (int i = 0; i < 3; i++) begin
      r = t.randomize();
      $display("randomize() returned %0d, len=%0d", r, t.len);
    end
    $finish;
  end
endmodule
