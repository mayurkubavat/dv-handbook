// tb_plusarg.sv -- which value $value$plusargs returns when a plusarg
// is given twice: it reads the first match on the command line. A
// harness that appends +seed=S after a testbench's own +seed=1 runs
// seed 1 every time.
module tb_plusarg;
  initial begin
    int seed;
    if (!$value$plusargs("seed=%d", seed)) seed = -1;
    $display("$value$plusargs(\"seed=%%d\") returned %0d", seed);
    $finish;
  end
endmodule
