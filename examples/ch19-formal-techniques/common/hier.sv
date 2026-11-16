// hier.sv -- two of the book's FIFOs in series, for a proof done
// block by block.
//
// fifo_ctr is one FIFO plus its occupancy model g, computed from the
// FIFO's ports alone, so that it survives when the FIFO is
// black-boxed. The contract of a FIFO is stated on g and the ports:
// empty exactly when g is 0, full exactly when g is DEPTH.
module fifo_ctr #(parameter int DEPTH = 16) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  localparam int CW = $clog2(DEPTH) + 1;
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic [CW-1:0] g;
  wire push = wr_en && !full;
  wire pop  = rd_en && !empty;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) g <= '0;
    else        g <= g + CW'(push) - CW'(pop);
endmodule

// pipe2: words move from the first FIFO to the second whenever the
// first has one and the second has room. G counts the words the pipe
// holds, from its own two ports.
module pipe2 #(parameter int DEPTH = 16) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  localparam int GW = $clog2(DEPTH) + 2;
  logic [7:0] mid;
  logic       e0, f1;
  wire move = !e0 && !f1;
  fifo_ctr #(.DEPTH(DEPTH)) u0 (.clk, .rst_n, .wr_en, .rd_en(move),
                                .wr_data, .rd_data(mid), .full,
                                .empty(e0));
  fifo_ctr #(.DEPTH(DEPTH)) u1 (.clk, .rst_n, .wr_en(move), .rd_en,
                                .wr_data(mid), .rd_data, .full(f1),
                                .empty);
  logic [GW-1:0] G;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) G <= '0;
    else        G <= G + GW'(wr_en && !full) - GW'(rd_en && !empty);
endmodule
