// tb_ignore_assert.sv -- the same value as an ignore_bins, with an
// immediate assertion beside the sample: the check fails whether or
// not coverage is on, because it does not live in the coverage code.
module tb_ignore_assert;
  bit [2:0] cmd;
  bit       cov_on = 1;

  covergroup cg;
    cp: coverpoint cmd {
      bins        ok[]     = {[0:6]};
      ignore_bins reserved = {7};        // not counted, and not an error
    }
  endgroup
  cg g;

  task drive(input bit [2:0] c);
    cmd = c;
    assert (cmd != 7)                    // the checker, outside the gate
      else $error("check failed: cmd 7 is reserved");
    if (cov_on) g.sample();
    $display("drove cmd %0d", c);
  endtask

  initial begin
    void'($value$plusargs("cov=%d", cov_on));
    g = new;
    drive(3'd3);
    drive(3'd7);
    $display("end of test, no check failed");
    $finish;
  end
endmodule
