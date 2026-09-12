interface bus_if(input logic clk); logic valid; logic [7:0] data; logic ready; endinterface
module top; logic clk = 0; always #5 clk <= ~clk; bus_if b(clk);
  always_ff @(posedge clk) b.ready <= b.valid;
  initial begin b.valid = 0; b.data = 0; @(posedge clk); #1 b.valid = 1; b.data = 8'h5A;
    @(posedge clk); @(posedge clk); #1;
    if (b.ready==1 && b.data==8'h5A) $display("PROBE j10a PASS"); else $display("PROBE j10a FAIL"); $finish; end
endmodule
