// A modport that carries a clocking block, which is how the standard
// says a testbench's view of an interface is meant to be declared.
interface bus (input logic clk);
  logic [7:0] d;
  clocking cb @(posedge clk);
    output d;
  endclocking
  modport tb (clocking cb);
endinterface
module top;
  logic clk = 0;
  bus b (.clk);
  always #5 clk <= ~clk;
  initial begin
    @(b.cb); b.cb.d <= 8'h5A;
    @(b.cb); @(b.cb);
    if (b.d == 8'h5A) $display("PROBE modport_clocking PASS");
    else $display("PROBE modport_clocking FAIL");
    $finish;
  end
endmodule
