// tb_bit.sv -- the reset line declared two-state.
//
// `bit rst_n` starts at 0, which is the active level. The testbench then
// writes 0 to it: no transition, so no `negedge rst_n` event, so the
// asynchronous reset block never runs. The register is never loaded with
// its reset value. On a two-state simulator this is the same on every run.
module tb_bit;
  logic       clk = 0;
  bit         rst_n;
  logic [7:0] d = 8'h00, q;
  dut_reg u (.clk, .rst_n, .d, .q);
  always #5 clk <= ~clk;
  initial begin
    rst_n = 0;            // 0 -> 0: not an edge
    #2 $display("tb_bit:   q=%02h, no clock edge yet %0s", q,
                 q === 8'hA5 ? "(reset happened)" : "(reset never happened)");
    rst_n = 1;
    $finish;
  end
endmodule
