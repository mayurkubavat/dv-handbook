// tb_clocking.sv -- sampling before the edge, driving after it.
//
// A clocking block names a clock and says, for each signal, when the
// testbench reads it and when its writes land. `input #1step` reads the
// value from just before the edge; `output #0` writes just after it. The
// testbench then never races the design at the edge (@sec-ch04-boundary):
// it reads what the design had settled and drives what the design will
// see next.
module dut_inc (input logic clk, input logic [7:0] d, output logic [7:0] q);
  always_ff @(posedge clk) q <= d + 8'd1;
endmodule

module tb_clocking;
  logic clk = 0;
  logic [7:0] d = 0, q;
  dut_inc u (.clk, .d, .q);
  always #5 clk <= ~clk;
  clocking cb @(posedge clk);
    default input #1step output #0;
    input  q;
    output d;
  endclocking
  initial begin
    repeat (3) begin
      @(cb);
      $display("t=%0d ns  read q=%0d (settled before this edge)  drive d=%0d",
               $time, cb.q, cb.q + 8'd10);
      cb.d <= cb.q + 8'd10;
    end
    @(cb);
    $display("t=%0d ns  read q=%0d", $time, cb.q);
    $finish;
  end
endmodule
