// tb_silent_group.sv -- three covergroups on one byte stream. One is
// declared but never built, one is built but never sampled, one is
// built in new() and sampled by the monitor. The built-but-unsampled
// group reports 0.00 and prints nothing; the never-built group has no
// figure at all, and asking for one is a null dereference.
class byte_cov;
  byte b;                                // the byte the monitor saw

  covergroup g_never_built;              // declared, never assigned
    cp: coverpoint b { bins lo = {[0:63]}; bins mid = {[64:191]};
                       bins hi = {[192:255]}; }
  endgroup

  covergroup g_never_sampled;            // built, sample() never called
    cp: coverpoint b { bins lo = {[0:63]}; bins mid = {[64:191]};
                       bins hi = {[192:255]}; }
  endgroup

  covergroup g_live;                     // built and sampled
    cp: coverpoint b { bins lo = {[0:63]}; bins mid = {[64:191]};
                       bins hi = {[192:255]}; }
  endgroup

  function new();
    // g_never_built = new;  <- the line that was forgotten
    g_never_sampled = new;
    g_live = new;
  endfunction

  // The monitor calls this once per observed transaction.
  task observe(byte v);
    b = v;
    g_live.sample();
  endtask
endclass

module tb_silent_group;
  byte_cov cov;
  byte stream[6] = '{8'd5, 8'd40, 8'd63, 8'd200, 8'd250, 8'd255};

  initial begin
    cov = new;
    foreach (stream[i]) cov.observe(stream[i]);
    $display("transactions observed : %0d", $size(stream));
    $display("g_live                : %0.2f",
             cov.g_live.get_inst_coverage());
    $display("g_never_sampled       : %0.2f",
             cov.g_never_sampled.get_inst_coverage());
    $display("g_never_built is null : %0d", cov.g_never_built == null);
    $display("g_never_built         : asking anyway ...");
    $display("g_never_built         : %0.2f",
             cov.g_never_built.get_inst_coverage());
    $finish;
  end
endmodule
