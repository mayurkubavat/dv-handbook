// tb_sampling_forms.sv -- the same bytes sampled three ways: by a
// clocking event on the bus, by an explicit sample() from the monitor,
// and by sample(b, ok) with the monitor's valid flag as an argument.
// The third form is one covergroup type with two instances, each
// bound by a ref argument to its own lane-enable variable.
module tb_sampling_forms;
  bit  clk = 0;
  always #5 clk = ~clk;

  byte data;                             // the bus: idles at 8'hff
  bit  valid;                            // high for one cycle per byte
  bit  a_on, b_on;                       // lane enables, seen by ref

  // Form 1: sampled by the simulator on every posedge, valid or not.
  covergroup g_clocked @(posedge clk);
    cp: coverpoint data {
      bins q0 = {[0:63]};    bins q1 = {[64:127]};
      bins q2 = {[128:191]}; bins q3 = {[192:255]};
    }
  endgroup

  // Form 2: sampled when the monitor calls sample().
  covergroup g_explicit;
    cp: coverpoint data {
      bins q0 = {[0:63]};    bins q1 = {[64:127]};
      bins q2 = {[128:191]}; bins q3 = {[192:255]};
    }
  endgroup

  // Form 3: sample(b, ok) carries the value and its validity; the ref
  // argument is read live at every sample, not copied at new().
  covergroup g_fn(ref bit lane_on) with function sample(byte b, bit ok);
    cp: coverpoint b iff (ok && lane_on) {
      bins q0 = {[0:63]};    bins q1 = {[64:127]};
      bins q2 = {[128:191]}; bins q3 = {[192:255]};
    }
  endgroup

  g_clocked  gc;
  g_explicit ge;
  g_fn       ga, gb;
  int n_cycles, n_valid, n_calls, n_ok_a, n_ok_b;

  // The monitor: one process, one clock edge, three sampling forms.
  always @(posedge clk) begin
    n_cycles <= n_cycles + 1;
    n_calls  <= n_calls + 1;
    if (valid) begin n_valid <= n_valid + 1; ge.sample(); end
    ga.sample(data, valid); gb.sample(data, valid);
    if (valid && a_on) n_ok_a <= n_ok_a + 1;
    if (valid && b_on) n_ok_b <= n_ok_b + 1;
  end

  // The driver: a byte on cycles 1, 2, 4 and 6; the bus idles between.
  task drive(byte d, bit v);
    @(negedge clk); data = d; valid = v;
  endtask

  initial begin
    gc = new; ge = new; ga = new(a_on); gb = new(b_on);
    a_on = 1; b_on = 1;
    data = 8'hff; valid = 0;             // cycle 0: idle
    drive(8'd10, 1);                     // cycle 1: q0
    drive(8'd70, 1);                     // cycle 2: q1
    drive(8'hff, 0); b_on = 0;           // cycle 3: idle; lane B off
    drive(8'd130, 1);                    // cycle 4: q2
    drive(8'hff, 0);                     // cycle 5: idle
    drive(8'd140, 1);                    // cycle 6: q2 again
    drive(8'hff, 0);                     // cycle 7: idle
    @(negedge clk);
    $display("traffic: %0d cycles, %0d valid bytes, bus idles at ff",
             n_cycles, n_valid);
    $display("clocked @(posedge clk) : samples=%0d coverage=%0.2f",
             n_cycles, gc.get_inst_coverage());
    $display("explicit sample()      : samples=%0d coverage=%0.2f",
             n_valid, ge.get_inst_coverage());
    $display("sample(b, ok) lane A   : calls=%0d ok=%0d coverage=%0.2f",
             n_calls, n_ok_a, ga.get_inst_coverage());
    $display("sample(b, ok) lane B   : calls=%0d ok=%0d coverage=%0.2f",
             n_calls, n_ok_b, gb.get_inst_coverage());
    $display("verdict: the clocked form counted four idle cycles as traffic");
    $finish;
  end
endmodule
