// tb_regions.sv -- watch one timestep from several places at once.
//
// Every print below happens at the same simulation time. What separates
// them is which scheduling region each one lands in.
//
// Read the output next to the chapter's list of regions. Nothing here is
// asserted by the book; the simulator prints it.
//
// One thing to notice, because it is the rule rather than an accident: the
// two Active-region lines may appear in either order, and a different
// simulator or a different version may swap them. Only the order *between*
// regions is fixed. That is why the value of `b` read in the Active region
// is reliable and the order of the two lines around it is not.
module tb_regions;
  logic clk = 1'b0;
  logic a, b;

  initial forever #5 clk = ~clk;

  // Active: a blocking assignment takes effect where it is written, so the
  // read below sees the new value.
  always @(posedge clk) begin
    a = 1'b1;
    $display("  [active]    just assigned a=%0b with =", a);
  end

  // The non-blocking update is scheduled, not performed, so a read in the
  // Active region still sees the old value.
  always @(posedge clk) begin
    b <= 1'b1;
    $display("  [active]    just assigned b<=1, b is still %0b", b);
  end

  // $strobe waits until the non-blocking updates have been applied, which
  // is why it is the one to reach for when printing clocked values.
  always @(posedge clk)
    $strobe("  [postponed] $strobe sees b=%0b, after the update", b);

  initial begin
    $display("one timestep, printed from several places:");
    @(posedge clk);
    #1 $display("  [next step] a=%0b b=%0b", a, b);
    $finish;
  end
endmodule
