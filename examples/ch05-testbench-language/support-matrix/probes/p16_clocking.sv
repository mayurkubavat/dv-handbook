// clocking block in an interface, driven and sampled by a testbench
interface bus_if(input logic clk);
  logic       valid;
  logic [7:0] data;
  logic       ready;
  clocking cb @(posedge clk);
    default input #1step output #0;
    output valid, data;
    input  ready;
  endclocking
endinterface

module dut(input logic clk, input logic valid, input logic [7:0] data, output logic ready);
  always_ff @(posedge clk) ready <= valid;
endmodule

module top;
  logic clk = 0;
  always #5 clk <= ~clk;
  bus_if b(clk);
  dut u(.clk(clk), .valid(b.valid), .data(b.data), .ready(b.ready));
  initial begin
    b.cb.valid <= 0; b.cb.data <= 0;
    @(b.cb); b.cb.valid <= 1; b.cb.data <= 8'h77;
    @(b.cb); @(b.cb);
    $display("cb.ready=%0d data=%h", b.cb.ready, b.data);
    if (b.cb.ready == 1 && b.data == 8'h77) $display("PROBE p16 PASS");
    else $display("PROBE p16 FAIL");
    $finish;
  end
endmodule
