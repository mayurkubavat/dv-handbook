// tb_auto_bins.sv -- what a coverpoint with no bins measures, and the
// bin range from the opener. A 32-bit address with automatic bins is
// 100% after 64 values; option.auto_bin_max moves the figure. Then a
// 6-bit depth with its bound written 2^(w)-1 and 2**(w)-1.
module tb_auto_bins;
  bit [31:0] addr;
  covergroup g_auto;                     // default auto_bin_max is 64
    cp: coverpoint addr;
  endgroup
  covergroup g_auto16;
    cp: coverpoint addr { option.auto_bin_max = 16; }
  endgroup

  localparam int Msb = 9, Lsb = 4;       // a 6-bit field, [9:4]
  bit [5:0] depth;
  covergroup g_xor;                      // ^ is XOR: 2 ^ (6 - 1) = 7
    cp: coverpoint depth { bins d[] = {[0:2^(Msb+1-Lsb)-1]}; }
  endgroup
  covergroup g_pow;                      // ** is power: 2**6 - 1 = 63
    cp: coverpoint depth { bins d[] = {[0:2**(Msb+1-Lsb)-1]}; }
  endgroup

  g_auto   a64, c64;
  g_auto16 a16, c16;
  g_xor    dx;
  g_pow    dp;

  initial begin
    a64 = new; a16 = new; c64 = new; c16 = new; dx = new; dp = new;

    // 64 addresses, one in each 2^26-wide automatic bin of 64.
    for (int i = 0; i < 64; i++) begin
      addr = 32'(i) << 26; a64.sample(); a16.sample();
    end
    $display("32-bit addr, 64 values one per 2^26 range");
    $display("  auto bins, default   : %0.2f", a64.get_inst_coverage());
    $display("  auto_bin_max = 16    : %0.2f", a16.get_inst_coverage());

    // 16 addresses, one in each 2^28-wide automatic bin of 16.
    for (int i = 0; i < 16; i++) begin
      addr = 32'(i) << 28; c64.sample(); c16.sample();
    end
    $display("32-bit addr, 16 values one per 2^28 range");
    $display("  auto bins, default   : %0.2f", c64.get_inst_coverage());
    $display("  auto_bin_max = 16    : %0.2f", c16.get_inst_coverage());

    // The opener's bound, with depths 0..7 sampled into both groups.
    for (int i = 0; i < 8; i++) begin
      depth = 6'(i); dx.sample(); dp.sample();
    end
    $display("6-bit depth, Msb = %0d, Lsb = %0d, depths 0..7 sampled",
             Msb, Lsb);
    $display("  2^(Msb+1-Lsb)-1  = %0d  bins d[] : %0.2f",
             2^(Msb+1-Lsb)-1, dx.get_inst_coverage());
    $display("  2**(Msb+1-Lsb)-1 = %0d  bins d[] : %0.2f",
             2**(Msb+1-Lsb)-1, dp.get_inst_coverage());
    $display("verdict: eight bins where sixty-four were meant, at 100.00");
    $finish;
  end
endmodule
