// tb_randomize_check.sv -- randomize() fails silently, and the fix is to
// read its return value every time.
//
// Four calls on one object. The first is legal. The second adds an
// inline constraint that contradicts the class's own, so the solver has
// no answer: the call returns 0 and changes nothing, and the object keeps
// the value from the call before. The third throws the return value away
// with void'(), which is the only way to compile an unchecked call, and
// hides the failure from the code; the tool's own warning goes to the
// log, where nothing in the testbench can act on it. The fourth is the
// idiom production libraries wrap in a macro: check, and stop on failure.
class txn;
  rand bit [7:0] len;
  constraint legal { len inside {[4:64]}; }
endclass

module tb_randomize_check;
  txn t;
  int  errors = 0;

  // The checked call: every randomize() in this book goes through
  // something like this, or through a macro that does the check.
  function automatic void randomize_or_fail(string where);
    if (t.randomize() != 1) begin
      errors++;
      $display("%s: randomize() returned 0, len still %0d", where, t.len);
    end
  endfunction

  initial begin
    t = new;
    // 1. legal: the solver picks a value inside [4:64]
    if (t.randomize() == 1)
      $display("legal:        returned 1, len=%0d", t.len);

    // 2. contradiction: the inline constraint cannot hold with `legal`
    if (t.randomize() with { len > 100; } != 1)
      $display("contradiction: returned 0, len still %0d (stale)", t.len);

    // 3. the same contradiction, return value discarded
    void'(t.randomize() with { len > 100; });
    $display("void'():      the tool warned, the code cannot tell, len=%0d",
             t.len);

    // 4. the checked idiom, with the contradiction and then without
    t.constraint_mode(0);              // drop `legal`: now > 100 is fine
    randomize_or_fail("checked");
    $display("checked:      returned 1, len=%0d, errors so far %0d",
             t.len, errors);
    t.constraint_mode(1);
    if (t.randomize() with { len > 100; } != 1) errors++;
    $display("the unchecked call left a stale value; checked calls: %0d",
             errors);
    $finish;
  end
endmodule
