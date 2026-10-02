// tb_fifo_cov.sv -- a coverage model for the Chapter 1 FIFO, sampled by
// a monitor that watches the ports and never by the driver. The driver
// pushes and pops at random (+bias=even: 50/50; +bias=push: push-heavy)
// for +n cycles; the monitor keeps its own occupancy count from the
// pushes and pops it sees accepted, and samples the covergroups once per
// clock. Nothing here checks the FIFO: this file measures stimulus.
`timescale 1ns/1ps

class fifo_cov;
  bit [4:0] occ;         // the monitor's occupancy: 0..16 needs five bits
  bit [1:0] op;          // {rd_en, wr_en} as requested on the ports
  bit       full, empty; // the DUT's flags at the same edge
  bit [2:0] level;       // occupancy band, for the fill transition

  covergroup fifo_cg;
    occupancy: coverpoint occ {
      bins empty   = {0};
      bins low     = {[1:7]};
      bins high    = {[8:14]};
      bins almost  = {15};
      bins full_16 = {16};
    }
    op_cp: coverpoint op {
      bins idle = {2'b00}; bins push = {2'b01};
      bins pop  = {2'b10}; bins both = {2'b11};
    }
    full_cp:  coverpoint full  { bins not_full  = {0}; bins full  = {1}; }
    empty_cp: coverpoint empty { bins not_empty = {0}; bins empty = {1}; }
    op_x_full:  cross op_cp, full_cp;
    op_x_empty: cross op_cp, empty_cp;
  endgroup

  // Sampled only when the band changes, so that consecutive samples are
  // consecutive bands. A transition between ranges of the occupancy
  // coverpoint itself does not build on Verilator 5.052.
  covergroup fill_cg;
    coverpoint level { bins climb = (0 => 1 => 2 => 3); }
  endgroup

  int push_while_full_at = -1;   // occupancy at the first push while full

  function new();
    fifo_cg = new;
    fill_cg = new;
    occ = 0; level = 0;
    fill_cg.sample();            // the band the FIFO starts in
  endfunction

  // Called by the monitor at every clock edge with what the ports show.
  function void observe(bit wr_en, bit rd_en, bit f, bit e);
    bit [2:0] next_level;
    op = {rd_en, wr_en}; full = f; empty = e;
    fifo_cg.sample();
    if (wr_en && f && push_while_full_at < 0) push_while_full_at = int'(occ);
    if (wr_en && !f) occ++;      // a push the contract says is accepted
    if (rd_en && !e) occ--;
    next_level = (occ == 0) ? 0 : (occ <= 7) ? 1 : (occ <= 14) ? 2 :
                 (occ == 15) ? 3 : 4;
    if (next_level != level) begin
      level = next_level;
      fill_cg.sample();
    end
  endfunction
endclass

module tb_fifo_cov;
  logic       clk = 0;
  logic       rst_n;
  logic       wr_en, rd_en;
  logic [7:0] wr_data, rd_data;
  logic       full, empty;
  int         n;
  string      bias;
  bit         done;
  fifo_cov    cov;

  fifo dut (.clk, .rst_n, .wr_en, .wr_data, .rd_en, .rd_data, .full,
            .empty);

  always #5 clk <= ~clk;

  // The driver: a new request at every falling edge.
  task automatic drive(int cycles);
    repeat (cycles) begin
      @(negedge clk);
      if (bias == "push") begin
        wr_en <= ($urandom_range(99) < 90);
        rd_en <= ($urandom_range(99) < 25);
      end else begin
        wr_en <= ($urandom_range(1) == 1);
        rd_en <= ($urandom_range(1) == 1);
      end
      wr_data <= 8'($urandom);
    end
  endtask

  // The monitor: at every rising edge, before the flops update, it
  // hands the request on the ports and the flags the DUT shows for it
  // to the coverage model. It samples exactly the n driven cycles.
  task automatic monitor();
    forever begin
      @(posedge clk);
      if (rst_n && !done) cov.observe(wr_en, rd_en, full, empty);
    end
  endtask

  initial begin
    if (!$value$plusargs("n=%d", n)) n = 200;
    if (!$value$plusargs("bias=%s", bias)) bias = "even";
    cov = new;
    rst_n = 0; wr_en = 0; rd_en = 0; wr_data = 0;
    fork monitor(); join_none
    repeat (2) @(posedge clk);
    rst_n <= 1;
    drive(n);
    @(negedge clk);
    wr_en <= 0; rd_en <= 0; done = 1;
    @(posedge clk);
    $display("+bias=%s +n=%0d: fifo_cg get_inst_coverage = %0.2f",
             bias, n, cov.fifo_cg.get_inst_coverage());
    if (cov.push_while_full_at >= 0)
      $display("covered: push while full at occupancy %0d",
               cov.push_while_full_at, " (a coverage hit, not a check)");
    else
      $display("not covered: push while full");
    $finish;
  end
endmodule
