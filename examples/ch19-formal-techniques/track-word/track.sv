// track.sv -- one tracked word through the book's FIFO: a symbolic
// constant, a free oracle and ghost state, for the data-independence
// check.
//
// sd is a free input the script holds constant (the stand-in for
// $anyconst, which the tool does not take). pick is a free oracle:
// the one push of sd it fires on is the tracked one, and it fires at
// most once while that word is inside (the !in_q guard). in_q says the
// tracked word is inside; ahead counts the words in front of it.
module track #(parameter int DEPTH = 16) (
  input  logic       clk, rst_n, wr_en, rd_en, pick,
  input  logic [7:0] wr_data, sd,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  localparam int AW = $clog2(DEPTH) + 1;
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic          in_q;
  logic [AW-1:0] ahead;
  wire take = pick && u.do_write && wr_data == sd && !in_q;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      in_q <= 1'b0; ahead <= '0;
    end else if (take) begin
      in_q <= 1'b1; ahead <= AW'(u.count) - AW'(u.do_read);
    end else if (in_q && u.do_read) begin
      if (ahead == '0) in_q <= 1'b0;
      else             ahead <= ahead - 1'b1;
    end
endmodule
