// tb_randc.sv -- randc walks every value once per cycle, and promises
// nothing about two randc variables constrained against each other.
class cycler;
  randc bit [2:0] c;                     // eight values, each once a cycle
endclass

class tied;
  randc bit [3:0] x;                     // sixteen values
  randc bit [1:0] y;                     // four values
  constraint c { x == 4'(y); }           // the two cycles cannot agree
endclass

module tb_randc;
  cycler cy;
  tied   td;
  int seen[8], distinct, fails;

  initial begin
    cy = new;
    for (int cyc = 0; cyc < 2; cyc++) begin
      for (int i = 0; i < 8; i++) seen[i] = 0;
      $write("cycle %0d:", cyc);
      for (int i = 0; i < 8; i++) begin
        if (cy.randomize() != 1) $fatal(1, "no solver");
        $write(" %0d", cy.c); seen[cy.c]++;
      end
      distinct = 0;
      for (int i = 0; i < 8; i++) if (seen[i] == 1) distinct++;
      $display("  (%0d distinct of 8)", distinct);
    end

    td = new; fails = 0;
    $write("x == y, 16 draws:");
    for (int i = 0; i < 16; i++) begin
      if (td.randomize() == 1) $write(" %0d", td.x);
      else begin $write(" -"); fails++; end
    end
    $display("  (%0d calls returned 0)", fails);
    $finish;
  end
endmodule
