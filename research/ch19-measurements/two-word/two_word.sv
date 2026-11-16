// two_word.sv -- two symbolic words through the book's FIFO.
// d1 and d2 are free inputs the script holds constant and distinct.
// The script's assumptions allow d1 to be pushed at most once and d2
// at most once, after d1; every other push carries some other value.
// The ghost flags record which of the two has gone in and come out;
// a1 and a2 count the words ahead of each while it is inside, as the
// tracked-word check of FM H does for one word.
module two_word #(parameter int DEPTH = 16) (
  input  logic       clk, rst_n, wr_en, rd_en,
  input  logic [7:0] wr_data, d1, d2,
  output logic [7:0] rd_data,
  output logic       full, empty
);
  fifo #(.WIDTH(8), .DEPTH(DEPTH)) u (.*);
  logic in1, in2, out1, out2;
  logic [4:0] a1, a2;
  wire push1 = u.do_write && wr_data == d1;
  wire push2 = u.do_write && wr_data == d2;
  wire pop1  = u.do_read  && rd_data == d1;
  wire pop2  = u.do_read  && rd_data == d2;
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) begin
      {in1, in2, out1, out2} <= '0; a1 <= '0; a2 <= '0;
    end else begin
      if (push1) in1  <= 1'b1;
      if (push2) in2  <= 1'b1;
      if (pop1)  out1 <= 1'b1;
      if (pop2)  out2 <= 1'b1;
      if (push1) a1 <= 5'(u.count) - 5'(u.do_read);
      else if (u.do_read && a1 != 0) a1 <= a1 - 5'd1;
      if (push2) a2 <= 5'(u.count) - 5'(u.do_read);
      else if (u.do_read && a2 != 0) a2 <= a2 - 5'd1;
    end
endmodule
