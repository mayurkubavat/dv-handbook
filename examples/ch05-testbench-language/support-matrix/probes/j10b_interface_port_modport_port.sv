interface bus_if(input logic clk); logic valid; logic [7:0] data; logic ready;
  modport dut (input clk, valid, data, output ready); endinterface
module dut(bus_if.dut b); always_ff @(posedge b.clk) b.ready <= b.valid; endmodule
module top; logic clk = 0; always #5 clk <= ~clk; bus_if b(clk); dut u(b);
  initial begin b.valid = 0; b.data = 0; @(posedge clk); #1 b.valid = 1; b.data = 8'h5A;
    @(posedge clk); @(posedge clk); #1;
    if (b.ready==1) $display("PROBE j10b PASS"); else $display("PROBE j10b FAIL"); $finish; end
endmodule
