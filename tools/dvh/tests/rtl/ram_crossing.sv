// ram_crossing.sv -- a value crossing clock domains through a RAM.
//
// Written on one clock and read on another, with no synchronizer. This
// went entirely unreported for a long time, and not because of anything in
// the domain map: an array survives `proc` as memory cells rather than
// registers, so the write port was not a register, its clock was not a
// domain at all, and the read port stopped the data walk as an opaque cell.
// A textbook asynchronous FIFO reported its pointer crossings and neither
// its data crossing nor its unreset storage.
module ram_crossing (input logic aclk, bclk, we, input logic [3:0] wa, ra,
                  input logic [7:0] wd, output logic [7:0] rd);
  logic [7:0] mem [16];
  always_ff @(posedge aclk) if (we) mem[wa] <= wd;
  always_ff @(posedge bclk) rd <= mem[ra];
endmodule
