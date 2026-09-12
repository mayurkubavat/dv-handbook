// tb_logic.sv -- the same testbench with the reset line four-state.
//
// `logic rst_n` starts at X on a four-state simulator, so the write of 0 is
// an X -> 0 transition, which is a negedge, and the reset runs. On a
// two-state simulator `logic` starts at 0 too, and the edge is missing
// exactly as it was for `bit`: the declaration did not change what the
// tool can see.
module tb_logic;
  logic       clk = 0;
  logic       rst_n;
  logic [7:0] d = 8'h00, q;
  dut_reg u (.clk, .rst_n, .d, .q);
  always #5 clk <= ~clk;
  initial begin
    rst_n = 0;            // X -> 0 on four-state; 0 -> 0 on two-state
    #2 $display("tb_logic: q=%02h, no clock edge yet %0s", q,
                 q === 8'hA5 ? "(reset happened)" : "(reset never happened)");
    rst_n = 1;
    $finish;
  end
endmodule
