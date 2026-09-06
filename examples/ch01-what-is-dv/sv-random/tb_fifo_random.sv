// tb_fifo_random.sv -- the test that found the bug.
//
// Three things this testbench has that the directed one does not:
//   stimulus  random write and read pressure, so occupancy wanders
//             across the whole range instead of staying at eight;
//   checker   an independent model of what a 16-entry FIFO must do,
//             compared against the design every cycle;
//   coverage  a record of the occupancy levels the test actually reached,
//             so a pass means something.
`timescale 1ns/1ps
module tb_fifo_random;
  localparam int DEPTH  = 16;
  localparam int CYCLES = 400;

  logic       clk = 0;
  logic       rst_n;
  logic       wr_en, rd_en;
  logic [7:0] wr_data, rd_data;
  logic       full, empty;

  fifo #(.DEPTH(DEPTH)) dut (.*);

  always #5 clk <= ~clk;

  // ---- checker state: the reference model is a queue, nothing more ----
  logic [7:0] model[$];
  int         errors = 0;
  int         writes = 0;
  bit         seen_occupancy[DEPTH+1];   // coverage: which levels we hit

  // The flags must agree with the model's occupancy after every edge.
  task automatic check_flags(int cycle);
    if (full !== (model.size() == DEPTH)) begin
      errors++;
      $display("FAIL cycle %0d, write %0d: full=%0b with %0d entries",
               cycle, writes, full, model.size());
      $display("     spec says full only at %0d entries", DEPTH);
    end
    if (empty !== (model.size() == 0)) begin
      errors++;
      $display("FAIL cycle %0d: empty=%0b with %0d entries",
               cycle, empty, model.size());
    end
  endtask

  function automatic int max_level();
    for (int i = DEPTH; i >= 0; i--) if (seen_occupancy[i]) return i;
    return 0;
  endfunction

  initial begin
    int seed = 1;
    int levels = 0;
    void'($value$plusargs("seed=%d", seed));
    void'($urandom(seed));

    rst_n = 0; wr_en = 0; rd_en = 0; wr_data = '0;
    repeat (2) @(posedge clk);
    rst_n = 1;

    for (int cycle = 0; cycle < CYCLES; cycle++) begin
      // ---- stimulus: bias toward writes early so the FIFO fills ----
      @(negedge clk);
      wr_en   = ($urandom_range(0, 99) < (cycle < 40 ? 90 : 55));
      rd_en   = ($urandom_range(0, 99) < 45);
      wr_data = 8'($urandom);

      // ---- checker, part 1: read data is visible before the edge ----
      if (rd_en && model.size() > 0 && rd_data !== model[0]) begin
        errors++;
        $display("FAIL cycle %0d: read %02h, expected %02h",
                 cycle, rd_data, model[0]);
      end

      // ---- checker, part 2: predict what the edge must have done ----
      @(posedge clk); #1;
      if (rd_en && model.size() > 0)     void'(model.pop_front());
      if (wr_en && model.size() < DEPTH) begin
        model.push_back(wr_data);
        writes++;
      end
      check_flags(cycle);
      seen_occupancy[model.size()] = 1;
      if (errors > 0) break;
    end

    // ---- coverage report: what did this run actually exercise? ----
    for (int i = 0; i <= DEPTH; i++) if (seen_occupancy[i]) levels++;
    $display("coverage: %0d of %0d occupancy levels reached, max %0d",
             levels, DEPTH + 1, max_level());

    if (errors == 0) $display("PASS: %0d cycles, %0d writes", CYCLES, writes);
    else begin
      $display("FAIL: stopped after %0d error(s)", errors);
      $fatal(1, "test failed");           // non-zero exit for make
    end
    $finish;
  end
endmodule
