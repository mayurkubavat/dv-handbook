// tb_ref.sv -- a `ref` argument, which needs an automatic lifetime.
//
// The argument is a reference into the caller's variable rather than a
// copy of it, so the task writes the caller's `v`. The standard allows
// `ref` only on an automatic subroutine; the reason this book gives is
// that a static one has nowhere safe to keep the reference between
// calls. Neither of this book's tools
// enforces that rule: one accepts `ref` on a static task in silence, the
// other rejects `ref` altogether, which is why this file runs on the
// default simulator only.
module tb_ref;
  task automatic bump(ref int x);
    x = x + 100;
  endtask
  int v = 1;
  initial begin
    bump(v);
    $display("after bump(ref v): v=%0d", v);
    $finish;
  end
endmodule
