// sink.sv -- a design that takes the interface as a port.
//
// It accepts a word whenever one is offered, one cycle later, and counts
// what it took. The port is `bus_if.dut`: the design cannot drive `valid`
// or `data`, and the compiler will say so if it tries.
module sink (bus_if.dut bus, output logic [7:0] taken);
  always_ff @(posedge bus.clk) begin
    bus.ready <= bus.valid;
    if (bus.valid && bus.ready) taken <= taken + 8'd1;
  end
  initial taken = 0;
endmodule
