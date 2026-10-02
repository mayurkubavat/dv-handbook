// tb_illegal.sv -- an illegal_bins value, sampled, stops the run with
// the tool's own message; with sampling turned off it says nothing.
module tb_illegal;
  bit [2:0] cmd;                         // 0..6 are commands, 7 is reserved
  bit       cov_on = 1;                  // +cov=0 turns sampling off

  covergroup cg;
    cp: coverpoint cmd {
      bins         ok[] = {[0:6]};
      illegal_bins bad  = {7};           // a run-time error, not a check
    }
  endgroup
  cg g;

  task drive(input bit [2:0] c);
    cmd = c;
    if (cov_on) g.sample();              // the UVM coverage_enable idiom
    $display("drove cmd %0d", c);
  endtask

  initial begin
    void'($value$plusargs("cov=%d", cov_on));
    g = new;
    drive(3'd3);
    drive(3'd7);                         // the reserved value
    $display("end of test, no check failed");
    $finish;
  end
endmodule
