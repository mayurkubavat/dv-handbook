// tb_packet_fifo.sv -- one packet from the port to the scoreboard.
//
// A producer class builds packets and pushes each onto the scoreboard's
// queue before driving it in through the clocking block. A consumer class
// reads words out and pops the queue: the word must match the packet at
// the head, or the order the FIFO promised has been broken. Everything the
// chapter taught is on this page: a packed struct, a class with a static
// member, a queue of handles, an interface held through a virtual
// interface, and a clocking block at the boundary.
// The scoreboard is an object of its own: a queue of handles, in send
// order, that the producer pushes and the consumer pops. Both hold a handle
// to the same scoreboard, so there is exactly one.
class scoreboard;
  packet expected [$];
endclass

class producer;
  virtual fifo_if vif;
  scoreboard sb;
  task run(int n);
    packet p;
    for (int i = 0; i < n; i++) begin
      p = new(i[1:0], i[5:0]);
      sb.expected.push_back(p);
      @(vif.cb);
      while (vif.cb.full) @(vif.cb);
      vif.cb.wr_en   <= 1;
      vif.cb.wr_data <= p.word;
      @(vif.cb);
      vif.cb.wr_en   <= 0;
      $display("sent     %s", p.str());
    end
  endtask
endclass

class consumer;
  virtual fifo_if vif;
  scoreboard sb;
  int errors = 0;
  task run(int n);
    packet p;
    word_t w;
    for (int i = 0; i < n; i++) begin
      @(vif.cb);
      while (vif.cb.empty) @(vif.cb);
      w = vif.cb.rd_data;
      vif.cb.rd_en <= 1;
      @(vif.cb);
      vif.cb.rd_en <= 0;
      p = sb.expected.pop_front();
      if (p.same(w)) $display("received %s  ok", p.str());
      else begin
        errors++;
        $display("received kind=%0d seq=%0d but expected %s",
                 w.kind, w.seq, p.str());
      end
    end
  endtask
endclass

module tb_packet_fifo;
  localparam int N = 6;
  logic clk = 0;
  always #5 clk <= ~clk;
  fifo_if #(.WIDTH(8)) bus (.clk);
  fifo #(.WIDTH(8), .DEPTH(4)) dut (
    .clk, .rst_n(bus.rst_n), .wr_en(bus.wr_en), .wr_data(bus.wr_data),
    .rd_en(bus.rd_en), .rd_data(bus.rd_data), .full(bus.full),
    .empty(bus.empty));

  scoreboard sb   = new;
  producer   prod = new;
  consumer   cons = new;
  initial begin
    prod.vif = bus; cons.vif = bus;
    prod.sb = sb;   cons.sb = sb;
    bus.cb.rst_n <= 0; bus.cb.wr_en <= 0; bus.cb.rd_en <= 0;
    bus.cb.wr_data <= 0;
    repeat (2) @(bus.cb);
    bus.cb.rst_n <= 1;
    fork
      prod.run(N);
      cons.run(N);
    join
    $display("packets made: %0d, left on scoreboard: %0d, errors: %0d",
             packet::made, sb.expected.size(), cons.errors);
    $finish;
  end
endmodule
