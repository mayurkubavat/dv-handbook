// An asynchronous *load* rather than an asynchronous reset: the register
// takes another signal's value, not a constant. Yosys emits $aldff, whose
// asynchronous pins are ALOAD and AD. Two defects met here. Code that
// assumed every asynchronous register has ARST or CLR stopped with a
// traceback instead of a finding; and the loaded value arrives from a
// register on another clock, which is a crossing the data walk missed
// because AD was not on its list of data pins.
module async_load (
    input  logic aclk,
    input  logic bclk,
    input  logic load,
    input  logic [7:0] din,
    output logic [7:0] dout
);
  logic [7:0] staged;

  always_ff @(posedge aclk)
    staged <= din;

  always_ff @(posedge bclk or posedge load)
    if (load) dout <= staged;     // aclk's value, loaded asynchronously
    else      dout <= din;
endmodule
